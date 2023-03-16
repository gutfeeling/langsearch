import datetime
from difflib import SequenceMatcher
import logging
import os

from scrapy.exceptions import DropItem

from langsearch.pipelines.base import BasePipeline
from langsearch.pipelines.common.mixins.weaviatedb import WeaviateMixin

logger = logging.getLogger(__name__)


class BaseStoreItemPipeline(BasePipeline):
    INPUTS = {
        "text": "text",
        "url": "url",
    }
    CHANGED = "store_item_pipeline_changed"
    CLASS_SCHEMA = {
        "class": "CrawlData",
        "vectorizer": "none",
        "vectorIndexConfig": {
            "skip": True
        },
        "invertedIndexConfig": {
            "indexNullState": True
        },
        "properties": [
            {
                "name": "url",
                "description": "The URL containing the section",
                "dataType": ["string"],
            },
            {
                "name": "text",
                "description": "Text of the document, if available",
                "dataType": ["text"],
            },
            {
                "name": "last_seen",
                "description": "When this URL was last seen in the crawling process",
                "dataType": ["date"],
            },
        ],
    }
    DUPLICATE_CUTOFF = 95

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_schema = self.__class__.get_setting_from_partial_key(os.environ, "CLASS_SCHEMA")
        if isinstance(class_schema, str):
            class_schema = self.get_params_from_file(class_schema)
        self.class_schema = class_schema
        self.class_name = self.class_schema["class"]
        if not self.weaviate.class_exists(self.class_name):
            self.weaviate.create_class(self.class_schema)
        self.duplicate_cutoff = self.__class__.get_setting_from_partial_key(os.environ, "DUPLICATE_CUTOFF")

    @staticmethod
    def similarity(text1, text2):
        m = SequenceMatcher(None, text1, text2)
        return m.real_quick_ratio() * 100

    def get_all_data_obj_for_url(self):
        where_filter = {
            "path": ["url"],
            "operator": "Equal",
            "valueString": self.url
        }
        result = (
            self.weaviate.client.query
            .get(self.class_name, ["text"])
            .with_additional(["id"])
            .with_where(where_filter)
            .do()
        )
        return result["data"]["Get"][self.class_name]

    def apply(self, item, spider):
        if not hasattr(self, "url") or self.url is None:
            return item
        try:
            data = self.get_all_data_obj_for_url()
            count = len(data)
            if count > 1:
                message = f"Found {count} data obj for unique property URL {self.url} in class {self.class_name}"
                logger.warning(message)
                raise RuntimeError(message)
            elif count == 0:
                self.weaviate.client.data_object.create(
                    class_name=self.class_name,
                    data_object={
                        "url": self.url,
                        "text": self.text if hasattr(self, "text") else None,
                        "last_seen": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                )
                item[self.CHANGED] = True
                return item
            else:
                unique_id = data[0]["_additional"]["id"]
                if hasattr(self, "text"):
                    text = data[0]["text"]
                    if self.similarity(text, self.text) <= self.duplicate_cutoff:
                        self.weaviate.client.data_object.update(
                            class_name=self.class_name,
                            uuid=unique_id,
                            data_object={
                                "url": self.url,
                                "text": self.text,
                                "last_seen": datetime.datetime.now(datetime.timezone.utc).isoformat()
                            }
                        )
                        item[self.CHANGED] = True
                        return item
                self.weaviate.client.data_object.update(
                    class_name=self.class_name,
                    uuid=unique_id,
                    data_object={
                        "last_seen": datetime.datetime.now(datetime.timezone.utc).isoformat()
                    }
                )
                item[self.CHANGED] = False
                return item
        except:
            message = f"Error while processing item with URL {self.url}"
            logger.exception(message)
            raise DropItem(message)


class StoreItemPipeline(BaseStoreItemPipeline, WeaviateMixin):
    pass
