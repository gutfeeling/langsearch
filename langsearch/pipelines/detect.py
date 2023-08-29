import logging

from scrapy.exceptions import DropItem
from tika import detector

from langsearch.pipelines.types.enumerations import ItemType

logger = logging.getLogger(__name__)


class DetectItemTypePipeline:
    def process_item(self, item, spider):
        response = item["response"]
        try:
            content_type = response.headers["Content-Type"]
            if isinstance(content_type, bytes):
                content_type = content_type.decode()
            if content_type.startswith("text/html"):
                item["type"] = ItemType.HTML
                return item
        except KeyError:
            pass
        mime_type = detector.from_buffer(response.body)
        if mime_type == "text/html":
            item["type"] = ItemType.HTML
            return item
        elif mime_type.startswith("text"):
            item["type"] = ItemType.TEXT
            return item
        elif mime_type.startswith(("audio", "video")):
            item["type"] = ItemType.AUDIO
            return item
        elif mime_type.startswith("image"):
            item["type"] = ItemType.IMAGE
            return item
        else:
            item["type"] = ItemType.OTHER
            return item
        message = f"Item with url {response.url} could not be classified into a type"
        logger.warning(message)
        raise DropItem(message)
