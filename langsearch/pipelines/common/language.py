import logging

from langdetect import detect
from scrapy.exceptions import DropItem

from langsearch.pipelines.base import BasePipeline
from langsearch.exceptions import SettingsError


logger = logging.getLogger(__name__)


class LanguageFilterPipeline(BasePipeline):
    INPUTS = {
        "text": "text",
        "url": "url"
    }
    ALLOWED_LANGUAGES = None
    LANGUAGE = "language_filter_pipeline_language"

    def __init__(self, allowed_languages, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_languages = allowed_languages

    @classmethod
    def from_crawler(cls, crawler):
        allowed_languages = cls.get_setting_from_partial_key(crawler.settings, "ALLOWED_LANGUAGES")
        if not isinstance(allowed_languages, list) and allowed_languages is not None:
            raise SettingsError(
                f"setting with partial key ALLOWED_LANGUAGES of class {cls} must be a list or None, "
                f"got {type(allowed_languages)}"
            )
        return cls(allowed_languages)

    def apply(self, item, spider):
        if self.allowed_languages is None:
            return item
        else:
            if not hasattr(self, "text") or self.text is None:
                return item
            if not hasattr(self, "url"):
                return item
            try:
                language = detect(self.text)
            except:
                message = f"Language detection failed for url {self.url}"
                logger.exception(message)
                raise DropItem(message)
            else:
                if language in self.allowed_languages:
                    item[self.LANGUAGE] = language
                    return item
                else:
                    message = f"Language {language} not in allowed languages {self.allowed_languages} for url {self.url}"
                    logger.info(message)
                    raise DropItem(message)
