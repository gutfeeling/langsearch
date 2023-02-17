import logging

from lxml import etree
from scrapy.exceptions import DropItem

from langsearch.pipelines.base import BasePipeline

logger = logging.getLogger(__name__)


class HTMLFromTextPipeline(BasePipeline):
    INPUTS = {
        "text": "text",
        "url": "url"
    }
    HTML = "html_from_text_pipeline_html"

    def apply(self, item, spider):
        if not hasattr(self, "text") or self.text is None:
            return item
        try:
            parsed = etree.HTML(self.text)
        except:
            message = f"Failed to parse response text for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
        else:
            item[self.HTML] = etree.tostring(parsed, method="html", encoding=str)
            return item

