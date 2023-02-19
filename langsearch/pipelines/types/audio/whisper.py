from io import StringIO
import logging

import ffmpeg
import numpy as np
from scrapy.exceptions import DropItem
import whisper
from whisper.tokenizer import LANGUAGES
from whisper.utils import get_writer

from langsearch.exceptions import SettingsError
from langsearch.pipelines.base import BasePipeline


logger = logging.getLogger(__name__)


class WhisperPipeline(BasePipeline):
    INPUTS = {
        "body": "body",
        "url": "url"
    }
    TRANSCRIPTION = "whisper_pipeline_transcription"
    MODEL = "tiny"
    DECODING_OPTIONS = {}
    ALLOWED_LANGUAGES = list(LANGUAGES.keys())
    OUTPUT_FORMAT = "txt"

    def __init__(self, model, decoding_options, allowed_languages, output_format, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = whisper.load_model(model)
        self.decoding_options = whisper.DecodingOptions(**decoding_options)
        self.allowed_languages = allowed_languages
        self.writer = get_writer(output_format, output_dir="")  # We don't use the output dir

    @classmethod
    def from_crawler(cls, crawler):
        model = cls.get_setting_from_partial_key(crawler.settings, "MODEL")
        if not isinstance(model, str):
            raise SettingsError(
                f"setting with partial key MODEL of class {cls} must be a str, "
                f"got {type(model)}"
            )
        decoding_options = cls.get_setting_from_partial_key(crawler.settings, "DECODING_OPTIONS")
        if not isinstance(decoding_options, dict):
            raise SettingsError(
                f"setting with partial key DECODING_OPTIONS of class {cls} must be a dict, "
                f"got {type(decoding_options)}"
            )
        allowed_languages = cls.get_setting_from_partial_key(crawler.settings, "ALLOWED_LANGUAGES")
        if not isinstance(decoding_options, list):
            raise SettingsError(
                f"setting with partial key ALLOWED_LANGUAGES of class {cls} must be a list, "
                f"got {type(allowed_languages)}"
            )
        output_format = cls.get_setting_from_partial_key(crawler.settings, "OUTPUT_FORMAT")
        allowed_output_formats = ["txt", "vtt", "srt", "tsv"]
        if output_format not in allowed_output_formats:
            raise SettingsError(
                f"setting with partial key OUTPUT_FORMAT of class {cls} must be one of {allowed_output_formats}, "
                f"got {output_format}"
            )
        return cls(model, decoding_options, allowed_languages, output_format)

    def load_audio(self):
        try:
            out, _ = (
                ffmpeg.input("pipe:", threads=0)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=16000)  # sample rate is hardcoded in whisper
                .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=self.body)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

    def apply(self, item, spider):
        if not hasattr(self, "body") or self.body is None:
            return item
        if not hasattr(self, "url"):
            return item
        try:
            audio = self.load_audio()
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            # TODO: We are doing language detection twice, once here and once in transcribe(). Make this more optimal.
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            if detected_lang not in self.allowed_languages:
                logger.info(f"Detected language {detected_lang} of audio at URL {self.url} "
                            f"is not in allowed languages {self.allowed_languages}"
                            )
                return item
            result = self.model.transcribe(mel, self.decoding_options)
            text_stream = StringIO()
            self.writer.write_result(result, file=text_stream)
            item[self.TRANSCRIPTION] = text_stream.getvalue()
            return item
        except:
            message = f"Whisper failed to extract text for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
