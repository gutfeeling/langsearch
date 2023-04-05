from langsearch.pipelines.common.index import SimpleIndexPipeline
from langsearch.pipelines.common.storeitem import StoreItemPipeline
from langsearch.pipelines.common.textsplitter import TextSplitterPipeline
from langsearch.pipelines.types.audio.whisper import WhisperPipeline
from langsearch.pipelines.types.enumerations import ItemType


class GenericAudioPipeline:
    """
    Built-in pipelines should always use priorities between 400 and 600.
    """
    ITEM_TYPE = ItemType.AUDIO

    ITEM_PIPELINES = {
        WhisperPipeline: 400,
        TextSplitterPipeline: 410,
        StoreItemPipeline: 420,
        SimpleIndexPipeline: 430
    }

    WHISPER_PIPELINE_INPUTS = {
        "body": lambda item: getattr(item["response"], "body"),
        "url": lambda item: getattr(item["response"], "url")
    }

    TEXT_SPLITTER_PIPELINE_INPUTS = {
        "text": WhisperPipeline.TRANSCRIPTION,
        "url": lambda item: getattr(item["response"], "url")
    }

    STORE_ITEM_PIPELINE_INPUTS = {
        "text": WhisperPipeline.TRANSCRIPTION,
        "url": lambda item: getattr(item["response"], "url")
    }

    SIMPLE_INDEX_PIPELINE_INPUTS = {
        "sections": TextSplitterPipeline.SECTIONS,
        "url": lambda item: getattr(item["response"], "url"),
        "changed": StoreItemPipeline.CHANGED
    }

    PIPELINE_INPUTS = {
        WhisperPipeline: WHISPER_PIPELINE_INPUTS,
        TextSplitterPipeline: TEXT_SPLITTER_PIPELINE_INPUTS,
        StoreItemPipeline: STORE_ITEM_PIPELINE_INPUTS,
        SimpleIndexPipeline: SIMPLE_INDEX_PIPELINE_INPUTS
    }
