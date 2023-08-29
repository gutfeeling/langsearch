import logging

from lxml import etree
from scrapy.exceptions import DropItem

from langsearch.pipelines.base import BasePipeline

logger = logging.getLogger(__name__)


class FixHTMLPipeline(BasePipeline):
    INPUTS = {
        "html": "html",
        "url": "url"
    }
    FIXED_HTML = "fix_html_pipeline_html"

    def apply(self, item, spider):
        if not hasattr(self, "html") or self.html is None:
            return item
        try:
            parsed = etree.HTML(self.html)
        except:
            message = f"Failed to parse response html for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
        else:
            item[self.FIXED_HTML] = etree.tostring(parsed, method="html", encoding=str)
            return item

