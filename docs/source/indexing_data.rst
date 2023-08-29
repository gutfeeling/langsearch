Indexing Data
=============

Introduction
------------

After you have :doc:`gathered the data <gathering_data>`, the next step is to index the data in a vector database.

In LangSearch, this works as follows. In the data gathering phase, you wrote a crawler that crawled webpages or
collected files from the local filesystem. For each webpage or local file, the crawler creates an item, which is just a
Python ``dict`` containing data about the discovered webpage or local file.

The item is then sent by the crawler to an **item pipeline**. The item pipeline is specified in the setting
``ITEM_PIPELINES`` in the ``settings.py`` file in the Scrapy project. The item pipeline takes care of indexing the
incoming web data or local file.

The code below shows the simplest item pipeline in LangSearch, which indexes any HTML webpage, while discarding data of
any other MIME type.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericHTMLPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericHTMLPipeline)
    }

Once you run your crawler using

.. code-block:: console

    scrapy crawler <crawler_name>

the crawled data will be automatically indexed for you in a Weaviate vector database using the pipeline defined in the
``ITEM_PIPELINES`` setting.

Built-in pipelines
------------------

Let's consider what's involved in indexing a webpage, which has the mimetype ``text/html``. Here are the steps.

1. Boilerplate removal using a tool like Mozilla Readability
2. Text extraction from HTML markup using a tool like Inscriptis
3. Language based filtering (optional) using a tool like ``langdetect``.
4. Splitting extracted text into smaller sections
5. Section size based filtering (optional)
6. Saving extracted text to a database (to identify changes to the page when re-crawling)
7. Indexing the sections in a vector database. This is when vector embeddings are computed using a language model and
   stored in the vector database

As you can see, it's a multi step process involving many steps. We can represent it in a diagram as follows (optional
components are omitted).

.. figure:: ./images/html_pipeline.drawio.svg
    :align: center

    Components of ``GenericHTMLPipeline``

In LangSearch, we have a class called ``GenericHTMLPipeline`` that handles all of the steps above. You use it by
specifying the ``ITEM_PIPELINES`` setting as follows in the ``settings.py`` file.


.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericHTMLPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericHTMLPipeline)
    }

Don't worry about the ``DetectItemTypePipeline`` and the ``assemble()`` function just yet. We will come to them in a
bit.

For audio/video data, the steps and the tools needed to index the data look very slightly different.

.. figure:: ./images/audio_pipeline.drawio.svg
    :align: center

    Components of ``GenericAudioPipeline``

Just like the ``GenericTextPipeline``, we also provide a built-in class called ``GenericAudioPipeline`` that will do all
of the above steps for you. To use it, you need to specify your ``ITEM_PIPELINES`` as follows.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline
    from langsearch.pipelines.types.audio.audiopipeline import GenericAudioPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericAudioPipeline)
    }

Now imagine a scenario where the incoming data can be either audio or text. In this case, we need a combined pipeline
like the one shown below.

.. figure:: ./images/audio_plus_text_pipeline.drawio.svg
    :align: center

    Combined pipeline that can handle both text and audio

Here, the ``MIME type detector`` detects the MIME type of the incoming crawled data and sends it to the correct branch
of the pipeline.

The code to create this combined pipeline in LangSearch is as simple as the following.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericHTMLPipeline
    from langsearch.pipelines.types.audio.audiopipeline import GenericAudioPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericHTMLPipeline, GenericAudioPipeline)
    }

With this example, we can now finally understand what the ``DetectItemTypePipeline`` class and the ``assemble()``
function is doing. The ``DetectItemTypePipeline`` is basically the ``MIME type detector`` node in the last diagram. It
detects the MIME type of the incoming crawled data. The ``assemble()`` function creates a combined pipeline out of the
pipelines passed to it as an argument. The ``DetectItemTypePipeline`` class and the ``assemble()`` function together
ensure that the data goes through the right pipeline components for its MIME type.

We can extend this naturally to all the built-in pipelines in LangSearch as follows.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericHTMLPipeline
    from langsearch.pipelines.types.plaintext.plaintextpipeline import GenereicPlainTextPipeline
    from langsearch.pipelines.types.audio.audiopipeline import GenericAudioPipeline
    from langsearch.pipelines.types.image.imagepipeline import GenericImagePipeline
    from langsearch.pipelines.types.other.otherpipeline import GenericOtherPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericPlainTextPipeline, GenericHTMLPipeline, GenericAudioPipeline, GenericImagePipeline, GenericOtherPipeline)
    }

And just like that, you now have a pipeline that can index more than 1000 different MIME types including plain text,
html, audio/video, images, pdfs, powerpoint presentations, word documents etc.
