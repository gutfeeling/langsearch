import logging

from scrapy.exceptions import DropItem
from trafilatura import extract

from langsearch.exceptions import SettingsError
from langsearch.pipelines.base import BasePipeline

logger = logging.getLogger(__name__)


class TrafilaturaPipeline(BasePipeline):
    INPUTS = {
        "html": "html",
        "url": "url"
    }
    TEXT_WITHOUT_BP = "trafilatura_pipeline_text_without_bp"
    EXTRACT_ARGUMENTS = {}

    def __init__(self, trafilatura_extract_arguments, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trafilatura_extract_arguments = trafilatura_extract_arguments

    @classmethod
    def from_crawler(cls, crawler):
        trafilatura_extract_arguments = cls.get_setting_from_partial_key(crawler.settings, "EXTRACT_ARGUMENTS")
        if not isinstance(trafilatura_extract_arguments, dict):
            raise SettingsError(
                f"setting with partial key EXTRACT_ARGUMENTS of class {cls} must be a dict, "
                f"got {type(trafilatura_extract_arguments)}"
            )
        return cls(trafilatura_extract_arguments)

    def apply(self, item, spider):
        if not hasattr(self, "html") or self.html is None:
            return item
        if not hasattr(self, "url"):
            return item
        args = {**self.trafilatura_extract_arguments, "output_format": "text"}
        try:
            text_without_bp = extract(self.html, **args)
        except:
            message = f"Trafilatura failed to extract text for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
        else:
            if isinstance(text_without_bp, str):
                item[self.TEXT_WITHOUT_BP] = text_without_bp
                return item
            else:
                message = f"Trafilatura extraction returned a non-string for url {self.url}"
                logger.warning(message)
                raise DropItem(message)
