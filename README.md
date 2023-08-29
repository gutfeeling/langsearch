# LangSearch: Easily create semantic search based LLM applications

## What is this?

LangSearch is a Python package for Retrieval Augmented Generation (RAG), which is useful for harnessing the power of 
Large Language Models (LLMs) like ChatGPT on non-public data. Unlike other packages that only take care of retrieval and generation,
this package also takes care of data discovery (e.g. crawling), data persistence (for updating data as it changes) and data 
preprocessing. This means you can get started with real world use cases quickly, with very little plumbing.

This package stands on the shoulders of giants, and uses the following well known Python packages and open source 
tools to do the heavy lifting.

- Scrapy for crawling
- Apache Tika for text extraction (more than 1000 MIME types supported)
- Mozilla Readability for boilerplate reduction
- Inscriptis for text extraction from HTML
- OpenAI Whisper for audio and video transcription
- Weaviate vector database for semantic search 
- Langchain for RAG

LangSearch is customizable and extensible. Almost every aspect is modifiable via settings. It also supports setting up 
custom crawlers and custom preprocessors.

## Show me the code

For instance, the code for doing RAG on the LangChain documentation is this simple.

### `crawler.py`

```python
from langsearch.spiders import WebSpider


class Crawler(WebSpider):
    name = "langchain"
```

### `settings.py`

```python
from langsearch.pipelines import assemble, DetectItemTypePipeline, GenericHTMLPipeline

LANGSEARCH_WEB_SPIDER_START_URLS = ["https://python.langchain.com/docs/get_started/introduction"]
LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = [
    "https://python\.langchain\.com/docs/get_started",
    "https://python\.langchain\.com/docs/modules",
    "https://python\.langchain\.com/docs/guides",
    "https://python\.langchain\.com/docs/ecosystem",
    "https://python\.langchain\.com/docs/additional_resources"
]
AUTOTHROTTLE_ENABLED = True

ITEM_PIPELINES = {
    DetectItemTypePipeline: 100,
    **assemble(GenericHTMLPipeline)
}
```

### On the command line

```
>>> from langsearch.chains import QAChain
>>> chain_output = QAChain()({"question": "How can I install langchain?"})
>>> print(chain_output["output_text"])
To install LangChain, you can use either conda or pip. 

If you prefer using conda, you can run the following command:

conda install langchain -c conda-forge

If you prefer using pip, there are two options depending on the modules you need. 

To install the modules needed for the common LLM providers, you can run:

pip install langchain[llms]

To install all modules needed for all integrations, you can run:

pip install langchain[all]

Note that if you are using zsh, you'll need to quote square brackets when passing them as an argument to a command. For example:

pip install 'langchain[all]'
```

## Installation

```
pip install langsearch
```

## Documentation 

Our documentation (WIP) can be found [here](https://langsearch.dibya.online). Code examples are in the
top-level `examples` folder.

## Features

1. Automatic and customizable data discovery for websites and local data (crawling)
2. Support for more than 1000 MIME types including html, pdf, docx, txt, png, mp3, mp4 etc.
3. Batteries included pipelines for preprocessing data
4. Crawl data persistence so that you can efficiently stay in sync with data
5. Embeddings using `text2vec-transformers` models (for text), and `CLIP` models for images.
6. RAG methods like simple QA and HyDE

## TODO

- [] Improve documentation
- [] Write tests
- [] Make CI pipeline for linting, building and testing
- [] Fine tuning language model on incoming data
- [] Handle metadata and use it in retrieval
- [] Allow authentication (login) before crawling starts 
- [] Support Pagerank + Vector Similarity Score + BM25 combinations
- [] Frontera integration? 
- [] GUI for settings
- [] Duplicate detection in images
- [] Ensemble methods in QA

## Contribute

We are very happy to get contributions from the community. Please feel free to try out the package, open bugs, 
pull requests (even improving the documentation helps a lot). You can contact me anytime at 
dibyachakravorty@gmail.com if you need any help. 