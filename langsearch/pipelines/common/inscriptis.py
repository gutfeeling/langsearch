import logging

from scrapy.exceptions import DropItem
from inscriptis import get_text, ParserConfig
from inscriptis.css_profiles import CSS_PROFILES

from langsearch.exceptions import SettingsError
from langsearch.pipelines.base import BasePipeline


logger = logging.getLogger(__name__)


class InscriptisPipeline(BasePipeline):
    INPUTS = {
        "html": "html",
        "url": "url"
    }
    EXTRACTED_TEXT = "inscriptis_pipeline_extracted_text"
    PARSER_CONFIG = ParserConfig(css=CSS_PROFILES["strict"].copy())

    def __init__(self, parser_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser_config = parser_config

    @classmethod
    def from_crawler(cls, crawler):
        parser_config = cls.get_setting_from_partial_key(crawler.settings, "PARSER_CONFIG")
        if not isinstance(parser_config, ParserConfig):
            raise SettingsError(
                f"setting with partial key PARSER_CONFIG of class {self.__class__} must be a inscriptis.ParserConfig, "
                f"got {type(parser_config)}"
            )
        return cls(parser_config)

    def apply(self, item, spider):
        if not hasattr(self, "html") or self.html is None:
            return item
        if not hasattr(self, "url"):
            return item
        try:
            extracted_text = get_text(self.html, self.parser_config)
        except:
            message = f"Inscriptis failed to extract text for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
        else:
            if isinstance(extracted_text, str):
                item[self.EXTRACTED_TEXT] = extracted_text
                return item
            else:
                message = f"Inscriptis extraction returned a non-string for url {self.url}"
                logger.warning(message)
                raise DropItem(message)
