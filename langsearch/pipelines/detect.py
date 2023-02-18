import logging

from scrapy.exceptions import DropItem
from tika import detector

from langsearch.pipelines.types.enumerations import ItemType

logger = logging.getLogger(__name__)


class DetectItemTypePipeline:
    def process_item(self, item, spider):
        response = item["response"]
        if hasattr(response, "text"):
            item["type"] = ItemType.TEXT
            return item
        elif hasattr(response, "body"):
            # TODO: Add timeout for docker compose like setup.
            mime_type = detector.from_buffer(response.body)
            if mime_type.startswith(("audio", "video")):
                item["type"] = ItemType.AUDIO
                return item
            else:
                item["type"] = ItemType.OTHER
                return item
        message = f"Item with url {response.url} could not be classified into a type"
        logger.warning(message)
        raise DropItem(message)
