Introduction
------------

LangSearch is a Python package that makes it easy to create semantic search based LLM applications. There are three
reasons why semantic search based LLM applications are interesting.

1. LLMs like ChatGPT are prone to hallucinations. If you ask them a question directly, they might confidently give you
   bullshit answers. A popular measure against hallucinations is to first run semantic search on your corpus to identify
   potential passages containing the answer, and then asking ChatGPT to answer the question based on those passages. You
   can also instruct ChatGPT to say "I don't know" if the answer is not contained in the passages. This significantly
   reduces hallucinations.

2. Currently available LLMs are trained on the public internet. Private data like company knowledge bases or data in
   personal files are outside its knowledge. One way to harness the power of ChatGPT on private data is to pass relevant
   snippets of private data in the context and ask ChatGPT to reason using it. Relevant snippets can be identified
   automatically by a combination of semantic search and other techniques.

3. Currently available LLMs also have a training cutoff. This means that it has no access to the latest information. One
   way of making ChatGPT aware of latest information is to index the latest information, identify relevant snippets
   using a combination of semantic search and other techniques, and pass it along in the context.

There are various tasks involved in building the backend of a semantic search based LLM application.

1. The first step is to gather the data that the application will be based on. If this data lives in websites (private
   websites included), which is the most common case, you need to use a web crawling framework like **Scrapy** to gather
   the data.
2. The data may be in various formats like ``html``, ``pdf``, ``pptx``, ``docx``, audio, video etc. LLMs only work with
   text, so you need to extract text from any kind of data that comes your way. For this, you can use **Apache Tika**,
   which can extract text from more than 1000 different formats. For text extraction from audio/video, the current best
   solution is **OpenAI Whisper**. For text extraction from HTML, there's the additional problem of boilerplate removal,
   and tools like **Mozilla Readability** can help with that.
3. Once text has been extracted, you need to split it up into passages and index the passages in a vector search engine
   like **Weaviate**. Vector search engines are the workhorses of semantic search. They store the embeddings of the
   text, and do semantic search by using nearest neighbor algorithms in the vector space of embeddings.
4. Finally, you need to query the LLM and pass along the information retrieved by semantic search into the context.
   Depending on the application and the LLM, you may need to make multiple dependent calls to the LLMs, an operation
   known as *chaining*. **LangChain** is currently the de-facto framework for doing that.

LangSearch helps with all the above steps by integrating the various different solutions into a single tool.

1. LangSearch can currently gather data from the web and local file systems. It is based on Scrapy, the powerful Python
   web crawling framework. You have the full power of Scrapy available. But we also provide two convenience classes
   ``WebSpider`` (for web data) and ``FileSpider`` (for local files) that helps you write crawlers with minimal code,
   and modify many aspects these crawlers by changing some intuitive settings. Therefore, you don't need to be a
   Scrapy expert to use LangSearch.

2. Once a piece of data is gathered by Scrapy, it is sent to a batteries-included built-in item pipeline, which
   orchestrates mime type detection (using Tika), text extraction (using Tika, Whisper, Readability and Inscriptis),
   filtering, persistence, and indexing (using Weaviate).

3. We provide convenience methods for doing QA (simple QA and also HyDE) against the built-in indexes. This uses
   **LangChain** under the hood.

One of the main contributions of LangSearch is the built-in pipeline that indexes data gathered by the crawler. Let's
look the features of the built-in pipeline.

1. MIME type detection is done automatically using Apache Tika, which can identify more than 1000 different formats.

2. Depending on the mime type, we automatically apply different text extraction methods. Currently, we have four
   different text extraction methods. For ``html``, we use a combination of **Readability** and **Inscriptis**, which
   produces good results for both text-heavy and code-heavy pages (and preserves syntactically significant whitespace).
   For audio/video data, we use OpenAI Whisper. For all other mime types, we use Apache Tika to extract text.

3. Text language and text size based filtering is applied according to user-selected settings.

4. Crawled data is automatically persisted in Weaviate. This allows us to automatically identify if a web page or file
   has changed since the last crawl, and only reindex changed pages when re-crawling. This can save money if paid
   embeddings API (e.g. the OpenAI Embeddings API) is used for calculating embeddings of the text passages.

5. Extracted text (after splitting into passages) is indexed in the Weaviate vector database. This is when embeddings
   are computed. We support all embeddings models supported by Weaviate, while using the free ``text2vec-transformers``
   models as the default. The exact model can be selected using a setting. The default index is a flat index of
   passages, but this can be changed to a tree-like index by swapping out a pipeline component.

6. Images are automatically indexed using CLIP models (thanks to Weaviate).

7. Most built-in pipeline component expose settings that can be adjusted to change how they work. For example, the
   component splitting text into passages creates passages with 512 tokens by default. But you can change this by
   changing a setting.

8. This system is fully extensible. You can add your own detection, text extraction or indexing mechanisms by extending
   the built-in pipeline components, or adding your own pipeline components to the built-in pipelines, or by creating
   your own pipeline completely from scratch.
