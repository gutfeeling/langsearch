# LangSearch: Easy semantic search using large language models

## Spiders 

### Webspider

#### Usage 

```
from langsearch.spiders.webspider import WebSpider


class MyWebSpider(WebSpider):
    name = "my_web_spider"
```

#### Settings for `WebSpider`

1. `LANGSEARCH_WEB_SPIDER_START_URLS`: list of seed URLs
2. `LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW`: list of regex patterns that absolute URLs must match to be extracted and 
followed
3. `LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY`: list of regex patterns. Matching links will not be extracted and followed. 
Has precedence over `LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW`

If you already have a list of target URLs, use the following settings in `settings.py`.

```
# You can also write code in settings.py e.g. to load START_URLS from a file
LANGSEARCH_WEB_SPIDER_START_URLS = ["<first_link>", "<second_link>", ... ]
LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = []
# We use an all-matching regex to ensure that only links in START_URLS are downloaded and no further links are followed
LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY = [".*"]
```

Here is an example for the second use case, where you don't have a list of target URLs but want to auto-discover links
by crawling from some seed URLs.

```
LANGSEARCH_WEB_SPIDER_START_URLS = ["https://docs.python.org"]
# Follow links to docs.python.org only. Links to wiki.python.org will not be extracted or followed, for example.
LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = ["docs.\python.\org"]
# Deny old documentation versions and non-english pages
LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY = ["docs\.python\.org(?!/3/)",
                                        "/es|fr|ja|ko|pt-br|tr|zh-cn|zh-tw/",
                                        ]
```

### Filespider

#### Usage 

```
from langsearch.spiders.filespider import FileSpider


class MyFileSpider(FileSpider):
    name = "my_file_spider"
```

#### Settings for `FileSpider`

1. `LANGSEARCH_FILE_SPIDER_START_FOLDERS`: list of folders to start from
2. `LANGSEARCH_FILE_SPIDER_FOLLOW_SUBFOLDERS`: boolean that indicates whether documents in subfolders will be fetched
3. `LANGSEARCH_FILE_SPIDER_FOLLOW_SYMLINKS`: boolean that indicates whether symbolic links will be followed
4. `LANGSEARCH_FILE_SPIDER_ALLOW`: list of regex that the absolute filepath (including extension) must match to be fetched
5. `LANGSEARCH_FILE_SPIDER_DENY`: absolute filepaths (including extension) matching any regex in this list will not be 
fetched. Has precedence over `LANGSEARCH_FILE_SPIDER_ALLOW`.

## Middlewares

### Spider Middlewares

#### RegexFilterMiddleware

##### Usage 

Include the following in your `settings.py`

```
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,   # Disable scrapy's OffsiteMiddleware
    'langsearch.middlewares.spider_middlewares.RegexFilterMiddleware': 500,    # Use langsearch's RegexFilterMiddleware instead
}
```

##### Settings

1. `LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW`
2. `LANGSEARCH_REGEX_FILTER_MIDDLEWARE_DENY`

## Pipelines

Include the following in your `settings.py`

```
ITEM_PIPELINES = {
   # The item that you send down the pipeline must have the fields "body", "text" and "url"
   # this pipeline detects the item type and sends it down the processors that handle that type
   # must be the first one in the list
   "langsearch.pipelines.DetectItemTypePipeline": 100,   
   # this builds a pipeline placing all components in the correct order 
   **assemble(pipelines=[TextPipeline,    # Add the pipelines for the types you want extracted
                         AudioVideoPipeline,   # This one extracts text from audio and video
                         OtherPipeline
                         ],
               )                          
   # attributes in item are transparently passed though
}
```

### Available settings

```
LANGSEARCH_TRAFILATURA_PIPELINE_EXTRACT_ARGUMENTS = {...}


LANGSEARCH_WHISPER_PIPELINE_ALLOWED_LANGUAGES=[...]
LANGSEARCH_WHISPER_PIPELINE_MODEL=...

LANGSEARCH_TEXT_LANGUAGE_FILTER_PIPELINE_ALLOWED_LANGUAGES=[...]

LANGSEARCH_STORE_ITEM_PIPELINE_EMBEDDING_MODEL=langsearch.EmbeddingModel.GPT3  # None will lead to no embedding and Weaviate's automatic embedding being used
LANGSEARCH_STORE_ITEM_PIPELINE_WEAVIATE_BASE_URL=http://localhost:...   # If not specified, will look for env variable
LANGSEARCH_STORE_ITEM_PIPELINE_DATABASE_URL=http://localhost:...   # If not specified, will look for env variable
LANGSEARCH_STORE_ITEM_PIPELINE_WEAVIATE_CLASS = ...  # If not specified, will use BOT_NAME setting
LANGSEARCH_STORE_ITEM_PIPELINE_DUPLICATE_CUTOFF = ...  # Default: 95
```

### `DryRunPipeline`

We additionally make a `DryRunPipeline` available that simply dumps the URLs to a file. This is useful to check that 
your allow/deny rules are working as expected.

### Philosophy for pipeline classes

1. Some pipelines have generic components that could have many implementations. For example, we use LLMs to
generate answers etc., and there are many LLMs. If there is a standard interface *already available* that abstracts out 
the various implementations, and this standard interface has everything we need to implement the pipeline, then we will
use that standard interface to write flexible pipeline classes. The exact implementation is then specified using 
settings or environment variables.



