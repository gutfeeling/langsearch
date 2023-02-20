import datetime
import logging
import os

from langchain.docstore.document import Document
from scrapy.exceptions import DropItem

from langsearch.pipelines.base import BasePipeline
from langsearch.pipelines.common.mixins.weaviatedb import WeaviateMixin


logger = logging.getLogger(__name__)


class BaseSimpleIndexPipeline(BasePipeline):
    INPUTS = {
        "url": "url",
        "sections": "sections",
        "changed": "changed"
    }
    CLASS_SCHEMA = {
        "class": "Section",
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False,
            }
        },
        "properties": [
            {
                "name": "url",
                "description": "The URL containing the section",
                "dataType": ["string"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                    }
                },
            },
            {
                "name": "section",
                "description": "Section text",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False
                    }
                },
            },
            {
                "name": "last_seen",
                "description": "When this URL was last seen in the crawling process",
                "dataType": ["date"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                    }
                },
            }
        ],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_schema = self.__class__.get_setting_from_partial_key(os.environ, "CLASS_SCHEMA")
        if isinstance(class_schema, str):
            class_schema = self.get_params_from_file(class_schema)
        self.class_schema = class_schema
        self.class_name = self.class_schema["class"]
        if not self.weaviate.class_exists(self.class_name):
            self.weaviate.create_class(self.class_schema)

    def create_or_change(self):
        self.weaviate.client.batch.delete_objects(
            class_name=self.class_name,
            where={
                "path": ["url"],
                "operator": "Equal",
                "valueString": self.url
            }
        )
        self.weaviate.add(
            class_name=self.class_name,
            data=[
                {
                    "url": self.url,
                    "section": section,
                    "last_seen": datetime.datetime.now(datetime.timezone.utc).isoformat()
                } for section in self.sections
            ]
        )

    def apply(self, item, spider):
        if not hasattr(self, "url"):
            return item
        if not hasattr(self, "sections"):
            return item
        try:
            if hasattr(self, "changed") and not self.changed:
                self.weaviate.update_property_with_current_datetime(
                    class_name=self.class_name,
                    where={
                        "path": ["url"],
                        "operator": "Equal",
                        "valueString": self.url
                    },
                    property_name="last_seen"
                )
            else:
                self.create_or_change()
        except:
            message = f"Error while processing item with URL {self.url}"
            logger.exception(message)
            raise DropItem(message)

    def get_similar_documents(self, text, top=4, token_limit=None, length_function=None):
        result = self.weaviate.get_near_text(self.class_name, text, ["url", "section", "last_seen"], top)
        if token_limit is not None:
            data_objects = []
            token_count = 0
            for res in result:
                section = res["section"]
                section_token_count = length_function(section)
                token_count += section_token_count
                if token_count > token_limit:
                    return data_objects
                data_objects.append(res)
            result = data_objects
        return [Document(page_content=item["section"], metadata={"source": item["url"]})
                for item in result
                ]


class SimpleIndexPipeline(BaseSimpleIndexPipeline, WeaviateMixin):
    pass
