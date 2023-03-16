import datetime
from io import BytesIO, BufferedReader
import logging
import os

from scrapy.exceptions import DropItem
from weaviate.util import image_encoder_b64, image_decoder_b64

from langsearch.pipelines.base import BasePipeline
from langsearch.pipelines.common.mixins.weaviatedb import WeaviateMixin


logger = logging.getLogger(__name__)


class BaseImageIndexPipeline(BasePipeline):
    INPUTS = {
        "url": "url",
        "body": "body",
        "changed": "changed"
    }
    CLASS_SCHEMA = {
        "class": "Image",
        "vectorizer": "multi2vec-clip",
        "moduleConfig": {
            "multi2vec-clip": {
                "imageFields": [
                    "image"
                ],
            }
        },
        "properties": [
            {
                "name": "url",
                "description": "The URL of the image",
                "dataType": ["string"],
            },
            {
                "name": "image",
                "description": "Base 64 encoded image",
                "dataType": ["blob"],
            },
            {
                "name": "last_seen",
                "description": "When this URL was last seen in the crawling process",
                "dataType": ["date"],
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

    def apply(self, item, spider):
        if not hasattr(self, "url"):
            return item
        if not hasattr(self, "body"):
            return item
        try:
            if hasattr(self, "changed") and not self.changed:
                self.weaviate.update_property_with_current_datetime(
                    class_name=self.class_name,
                    where_filter={
                        "path": ["url"],
                        "operator": "Equal",
                        "valueString": self.url
                    },
                    property_name="last_seen"
                )
            else:
                with BytesIO(self.body) as f:
                    base_64_encoded_image = image_encoder_b64(BufferedReader(f))
                    self.weaviate.client.data_object.create(
                        class_name=self.class_name,
                        data_object={
                            "url": self.url,
                            "image": base_64_encoded_image,
                            "last_seen": datetime.datetime.now(datetime.timezone.utc).isoformat()
                        }
                    )
        except:
            message = f"Error while processing item with URL {self.url}"
            logger.exception(message)
            raise DropItem(message)

    def get_image_bytes(self, base_64_encoded_image):
        return image_decoder_b64(base_64_encoded_image)

    def get_similar_images_from_text(self, text, limit=4):
        return self.weaviate.get_similar(self.class_name, text, ["url", "image", "last_seen"], limit=limit)

    def get_similar_images_from_image(self, image, top=4):
        return self.weaviate.get_near_image(self.class_name, image, ["url", "image", "last_seen"], top)


class ImageIndexPipeline(BaseImageIndexPipeline, WeaviateMixin):
    pass
