import datetime
import os
import time

from requests.exceptions import ConnectionError, HTTPError
from weaviate import Client
from weaviate.util import image_encoder_b64


class WeaviateDB:
    def __init__(self, base_url):
        # TODO: Added timeout for docker compose like setup. Look for a better solution.
        # TODO: Use `startup_period` argument of `weaviate.Client` when it becomes available.
        for _i in range(20):
            try:
                self.client = Client(base_url)
            except (ConnectionError, HTTPError):
                time.sleep(1)
            else:
                break

    def class_exists(self, class_name):
        schema = self.client.schema.get()
        classes = [c["class"] for c in schema["classes"]]
        return class_name in classes

    def create_class(self, class_schema):
        self.client.schema.create_class(class_schema)

    def add(self, class_name, data, batch_size=5):
        self.client.batch.configure(batch_size=batch_size)
        with self.client.batch as batch:
            for data_object in data:
                batch.add_data_object(
                    class_name=class_name,
                    data_object=data_object
                )

    def update_property_with_current_datetime(self, class_name, where_filter, property_name):
        result = (
            self.client.query
            .get(class_name)
            .with_additional(["id"])
            .with_where(where_filter)
            .do()
        )
        for element in result["data"]["Get"][class_name]:
            unique_id = element["_additional"]["id"]
            self.client.data_object.update(
                class_name=class_name,
                uuid=unique_id,
                data_object={
                    property_name: datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
            )

    def get_near_text(self, class_name, similar_to, query_attrs, limit):
        near_text = {"concepts": [similar_to]}
        result = (
            self.client.query
            .get(class_name, query_attrs)
            .with_near_text(near_text)
            .with_limit(limit)
            .do()
        )
        return result["data"]["Get"][class_name]

    def get_near_image(self, class_name, similar_to, query_attrs, limit):
        near_image = {"image": image_encoder_b64(similar_to)}
        result = (
            self.client.query
            .get(class_name, query_attrs)
            .with_near_image(near_image)
            .with_limit(limit)
            .do()
        )
        return result["data"]["Get"][class_name]


class WeaviateMixin:
    WEAVIATE_BASE_URL = "http://localhost:8080"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        weaviate_base_url = self.__class__.get_setting_from_partial_key(os.environ, "WEAVIATE_BASE_URL")
        self.weaviate = WeaviateDB(weaviate_base_url)
