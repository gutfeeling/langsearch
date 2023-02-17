import os
import time

from requests.exceptions import ConnectionError, HTTPError
from weaviate import Client


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


class WeaviateMixin:
    WEAVIATE_BASE_URL = "http://localhost:8080"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        weaviate_base_url = self.__class__.get_setting_from_partial_key(os.environ, "WEAVIATE_BASE_URL")
        self.weaviate = WeaviateDB(weaviate_base_url)
