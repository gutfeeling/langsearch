import logging

from lxml import etree
from readabilipy import simple_json_from_html_string
from scrapy.exceptions import DropItem

from langsearch.pipelines.base import BasePipeline


logger = logging.getLogger(__name__)


class ReadabilityJSPipeline(BasePipeline):
    INPUTS = {
        "html": "html",
        "url": "url"
    }
    HTML_WITHOUT_BP = "readability_js_pipeline_text_without_bp"

    def apply(self, item, spider):
        if not hasattr(self, "html") or self.html is None:
            return item
        if not hasattr(self, "url"):
            return item
        try:
            html_without_bp = simple_json_from_html_string(self.html, use_readability=True)["content"]
        except:
            message = f"Readability JS failed to remove boilerplate for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
        else:
            try:
                parsed = etree.HTML(html_without_bp)
            except:
                message = f"Readability JS did not return valid HTML for {self.url}"
                logger.exception(message)
                raise DropItem(message)
            else:
                item[self.HTML_WITHOUT_BP] = html_without_bp
                return item
