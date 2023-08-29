``GenericHTMLPipeline``
=======================

``GenericHTMLPipeline`` indexes crawled data with MIME type ``text/html``. You can activate it by writing your
``ITEM_PIPELINES`` settings as follows.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericHTMLPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericTextPipeline)
    }

When used alone (like in the above code example), your pipeline will discard any crawled data that does not match the
MIME type ``text/html``.

``GenericHTMLPipeline`` consists of the following pipeline components applied in sequence.

1. ``FixHTMLPipeline``: Tries to fix broken HTML documents using ``lxml``.
2. ``PythonReadabilityPipeline``: Removes boilerplate from the ``HTML`` document.
3. ``InscriptisPipeline``: Extracts text from the ``HTML`` document.
4. ``TextSplitterPipeline``: Splits the extracted text into smaller passages.
5. ``StoreItemPipeline``: Stores the extracted text in a Crawl DB. The Crawl DB is used to make re-crawling more efficient.
6. ``SimpleIndexPipeline``: Indexes the text passages in the Weaviate vector database.

Service requirements
--------------------

The ``GenericHTMLPipeline`` expects a Weaviate database to be available. Therefore,
you need make a Weaviate instance available before running the ``scrapy crawl`` command.

To make a Weaviate database available, create a ``docker-compose.yml`` file and add the following services to it.

.. literalinclude:: /../../examples/quickstart/docker-compose.yml

Change the ``CLUSTER_HOSTNAME`` to any name you prefer.

This ``docker-compose.yml`` starts Weaviate with a configuration that works seamlessly with the
the pipeline components.

To make the Weaviate DB available, run the following command (you need to have Docker installed).

.. code-block:: console

    docker compose up

.. note::

    The ``DetectItemPipeline`` actually also needs the Apache Tika service to do its job. This service can be omitted in
    the special case when you expect your crawler to exclusively send items of mimetype ``text/html`` and these webpages
    are well behaved i.e. sends correct ``Content-Type`` headers. If your situation deviates from this special situation,
    the crawler will stop and complain that it can't find the Apache Tika service. To solve this, add the Apache Tika
    service to the ``docker-compose.yml`` file.

    .. literalinclude:: /../../examples/local_audio/docker-compose.yml

    Please set the following env vars before starting the crawl so that the crawler can access the Tika service.

    .. code-block:: console

        export TIKA_CLIENT_ONLY="True"
        export TIKA_SERVER_ENDPOINT="http://localhost:9998"
