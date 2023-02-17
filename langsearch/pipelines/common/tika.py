import logging

from scrapy.exceptions import DropItem
from tika import parser

from langsearch.pipelines.base import BasePipeline

logger = logging.getLogger(__name__)


class TikaPipeline(BasePipeline):
    INPUTS = {
        "body": "body",
        "url": "url"
    }
    XML_OUTPUT = "tika_pipeline_xml_output"

    def apply(self, item, spider):
        if not hasattr(self, "body") or self.body is None:
            return item
        if not hasattr(self, "url"):
            return item
        try:
            xml_output = parser.from_buffer(self.body, xmlContent=True)["content"]
        except:
            message = f"Tika failed to extract text for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
        else:
            if isinstance(xml_output, str):
                item[self.XML_OUTPUT] = xml_output
                return item
            else:
                message = f"Tika extraction returned a non-string for url {self.url}"
                logger.info(message)
                raise DropItem(message)
