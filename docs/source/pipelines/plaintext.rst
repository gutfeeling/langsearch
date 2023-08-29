``GenericPlainTextPipeline``
============================

``GenericPlainTextPipeline`` indexes crawled plaintext data. You can activate it by writing your
``ITEM_PIPELINES`` settings as follows.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline
    from langsearch.pipelines.types.plaintext.plaintextpipeline import GenereicPlainTextPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericPlainTextPipeline)
    }

When used alone (like in the above code example), your pipeline will discard any crawled data that's not plaintext.

``GenericPlainTextPipeline`` consists of the following pipeline components applied in sequence.

1. ``TextSplitterPipeline``: Splits the text into smaller passages.
2. ``StoreItemPipeline``: Stores the text in a Crawl DB. The Crawl DB is used to make re-crawling more efficient.
3. ``SimpleIndexPipeline``: Indexes the text passages in the Weaviate vector database.

Service requirements
--------------------

The ``GenericPlainTextPipeline`` expects a Weaviate database to be available. It also needs an Apache Tika service to be up
and running. Therefore, you need make these services available before running the ``scrapy crawl`` command.

To do that, create a ``docker-compose.yml`` file and add the following services to it.

.. literalinclude:: /../../examples/local_images/docker-compose.yml

Change the ``CLUSTER_HOSTNAME`` to any name you prefer.

This ``docker-compose.yml`` starts Weaviate and Apache Tika with a configuration that works seamlessly with the
the pipeline components.

To make the services available, run the following command (you need to have Docker installed).

.. code-block:: console

    docker compose up

Please set the following env vars before starting the crawl so that the crawler can access the Apache Tika service.

.. code-block:: console

    export TIKA_CLIENT_ONLY="True"
    export TIKA_SERVER_ENDPOINT="http://localhost:9998"
