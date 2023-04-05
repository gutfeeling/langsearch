Quickstart
==========

Introduction
------------

In this quickstart guide, we will use LangSearch to create a QA application using
`ChatGPT <https://openai.com/blog/chatgpt>`_. Specifically, we will ask
questions about the popular `LangChain <https://langchain.readthedocs.io/>`_ package, which was released *after*
ChatGPT's training cutoff. Therefore, ChatGPT does not know any information about LangChain a priori.

The QA application will have the following features.

1. The answers will contain less hallucinations than ChatGPT ordinarily produces
2. The answers will cite sources
3. The answers will always be up-to-date and correspond to the latest version of the documentation

Building such an application requires the following steps.

1. Crawling selected pages from the LangChain documentation. These pages will be used as the information source for
   question answering.
2. Removing boilerplate text from the downloaded HTML document to prevent information pollution.
3. Extracting the main text content from the HTML document.
4. Splitting long pages into smaller sections.
5. Indexing the sections in a vector database like `Weaviate <https://weaviate.io/developers/weaviate>`_.
6. Building a semantic search based QA app using Weaviate and ChatGPT.
7. Running the crawler process periodically to keep our data up-to-date. To make this cost-efficient (especially when
   using paid embeddings APIs), we need to keep a record of each crawl, so that we only re-index changed pages.

LangSearch makes the above steps easy and accessible. Let's see how by building the QA application from scratch.

We will start by installing LangSearch.

.. code-block:: console

    pip install langsearch

Then create a folder ``quickstart``  to hold our QA application.

.. code-block:: console

    mkdir quickstart && cd quickstart

Crawling selected pages of the LangChain documentation
------------------------------------------------------

LangSearch uses `Scrapy <https://docs.scrapy.org/en/latest/>`_ under the hood for crawling web pages. Every LangSearch
project starts by creating a scrapy project.

.. code-block:: console

    scrapy startproject langchain_qa

This will create a ``langchain_qa`` folder with the following content.

.. code-block::

    .
    ├── langchain_qa
    │   ├── __init__.py
    │   ├── items.py
    │   ├── middlewares.py
    │   ├── pipelines.py
    │   ├── settings.py
    │   └── spiders
    │       └── __init__.py
    └── scrapy.cfg

To crawl the LangChain website, we need to create a crawler. Create a file ``crawler.py`` inside the
``spiders`` folder, and put the following code in the file.

.. code-block:: py

    from langsearch.spiders import WebSpider

    class Crawler(WebSpider):
        name = "langchain"

That's our crawler.

We will control some important aspects of the crawling process in the ``settings.py`` file. So go over to that file
and add the following code.

.. code-block:: python

    LANGSEARCH_WEB_SPIDER_START_URLS = ["https://langchain.readthedocs.io/en/latest/"]
    LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = [
        "https://langchain\.readthedocs\.io/en/latest/modules",
        "https://langchain\.readthedocs\.io/en/latest/use_cases",
        "https://langchain\.readthedocs\.io/en/latest/reference",
        "https://langchain\.readthedocs\.io/en/latest/ecosystem"
    ]
    AUTOTHROTTLE_ENABLED = True

The above settings tells the crawler to start crawling from `<https://langchain.readthedocs.io/en/latest/>`_ and only
follow links that match the regular expressions in ``LANGSEARCH_WEBSPIDER_LINK_EXTRACTOR_ALLOW``.

The ``AUTOTHROTTLE_ENABLED = True`` setting is a Scrapy setting that ensures that we don't hit the website too hard.

Removing boilerplate, extracting text, splitting text and indexing
------------------------------------------------------------------

LangSearch provides generic pipelines that orchestrate boilerplate removal, text extraction, text splitting and indexing
for various mime types. Therefore, you only need a couple of lines of code in the ``settings.py`` file for all these
steps.

.. code-block:: python

    from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericTextPipeline

    ITEM_PIPELINES = {
        DetectItemTypePipeline: 100,
        **assemble(GenericTextPipeline)
    }


.. _crawl:

Running the crawler
-------------------

To run the crawler, first download `this docker compose file <https://example.org>`_ and place it in the ``quickstart`` folder. This docker
compose file is responsible for running the Weaviate vector database. Start the Weaviate instance by using the following
command (you need to have ``docker`` installed in your system).

.. code-block:: console

    docker compose up

Then start the crawl by going inside the Scrapy project i.e. the ``langchain_qa`` folder and issuing the following
command

.. code-block:: console

    scrapy crawl langchain

Create a QA app
---------------

Once the crawling has been done, you can immediately start using the index to answer questions.

First, make sure that your terminal knows your OpenAI API key.

.. code-block:: console

    export OPENAI_API_KEY="..."

Then simply import the ``QAChain`` class from LangSearch and start asking questions.

.. code-block:: python

    from langsearch.chains import QAChain

    chain_output = QAChain({"question": "How can I install langchain?"})
    print(chain_output["output_text"])

Here's how you can create a Streamlit app to get a web interface. First, install ``streamlit``.

.. code-block:: console

    pip install streamlit

Then put the code below in a file called ``webapp.py``.

.. code-block:: python

    import streamlit as st

    from langsearch.chains.qa import QAChain

    st.title("QA Demo")
    question = st.text_input("Ask any question about Langchain")
    if len(question) != 0:
        chain_output = QAChain()({"question": question})
        answer = chain_output["output_text"]
        sources = set([doc.metadata["source"] for doc in chain_output["docs"]])
        st.markdown(answer)
        for index, source in enumerate(sources):
            st.markdown(f"[{index + 1}] [{source}]({source})")

Then bring up the web app by issuing the following command.

.. code-block:: console

    streamlit run webapp.py

Keep your QA app up-to-date
---------------------------

Simply run the following command using ``chron`` or any other scheduler.

.. code-block:: python

    scrapy crawl langchain

This will only re-index (and compute embeddings) for pages that have changed since the last run.
