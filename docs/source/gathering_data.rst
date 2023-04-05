Gathering Data
==============

Introduction
------------

When you set out to build a semantic search based application, the first step is to gather the data that will be
indexed.

LangSearch can gather data that lives on :ref:`websites <web>` or :ref:`local file systems <file>` in any manner
determined by you. It does this by using Scrapy, a powerful Python web crawling framework.

For simple use cases, we offer two convenience classes ``WebSpider`` and ``FileSpider``, which makes it possible to
gather data by writing very little Scrapy code and mostly by changing some settings in a settings file.

For more complex use cases, you can write your spiders directly using Scrapy and make them as complex as they need to
be.

Let's look at the steps involved in creating a crawler.

Creating a Scrapy project
-------------------------

To gather data, the first step is always the same: creating a ``Scrapy`` project.

.. code-block::

    scrapy startproject <projectname>

This creates a folder ``<projectname>`` with the following content. ::

    .
    ├── <projectname>
    │   ├── __init__.py
    │   ├── items.py
    │   ├── middlewares.py
    │   ├── pipelines.py
    │   ├── settings.py
    │   └── spiders
    │       └── __init__.py
    └── scrapy.cfg

.. _web:

Crawling websites
-----------------

To crawl websites, we need to create a Python file inside the ``spiders`` folder. You can name this file however you
want. We will call it ``crawler.py`` for this example.

In the file, you need to write the following code to create a web crawler.

.. code-block:: python

    from langsearch.spiders import WebSpider

    class Crawler(WebSpider):
        name = "my_crawler"

The ``Crawler`` class is our web crawler. We named the class ``Crawler``, but you can name it however you want. This
class is basically just a ``WebSpider`` class, but with a unique ``name`` attribute set to ``my_crawler``. You can
choose this string freely. The ``name`` attribute is important when running the crawler, as we will find out later.

The ``WebSpider`` class defines a general-purpose crawler whose behavior can be controlled by adding some settings in
the ``settings.py`` file. The core behavior of this crawler is as follows.

1. It starts by visiting the page(s) listed in the setting ``LANGSEARCH_WEB_SPIDER_START_URLS``.
2. For each visited page, it extracts links from the page. You can also control which links are extracted using
   settings.
3. After the links have been extracted, the crawler visits each extracted link. Normally, links visited earlier in the
   process will not be visited again.
4. The above process continues until there are no more links left to visit.
5. Each page that the crawler visits is sent to an item pipeline for further processing.

``WebSpider`` settings
^^^^^^^^^^^^^^^^^^^^^^

Many aspects of the ``WebSpider``'s behavior can be influenced by adding settings to the ``settings.py`` file. All
such settings start with the prefix ``LANGSEARCH_WEB_SPIDER``. Here's the complete list of allowed settings.

``LANGSEARCH_WEB_SPIDER_START_URLS``

    This is a ``list`` containing the seed URLs that the crawler visits first. This is equivalent to setting
    the ``start_urls`` class variable in a Scrapy ``Spider``.

    This setting is required.

The settings below determine how the crawler extracts links to follow.  Under the hood, it uses Scrapy's
``LxmlLinkExtractor`` class to apply these settings

``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW``

    This is a ``list`` of regular expressions. For every visited page, the crawler will only extract links (absolute
    URLs) matching any of the regular expressions listed in this list. This maps to the ``allow`` argument of Scrapy's
    ``LxmlLinkExtractor``.

    The default value is an empty list ``[]``, meaning no links will be extracted.

``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY``

    This is a ``list`` of regular expressions. Links matching any of these regular expressions will not be extracted.
    This has precedence over ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW``. This setting is equivalent to setting the
    ``deny`` argument of Scrapy's ``LxmlLinkExtractor``.

    The default behavior is an empty list ``[]``, meaning no links are denied.

.. note::

    If you leave both ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW`` and ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY``
    unspecified, the crawl will end after visiting the start URLs. You need to specify something in
    ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW`` for the crawler to start extracting and following links. If you
    want to follow all links, use ``[".*"]``. But a more restrictive setting is recommended for most use cases, since
    websites contain a lot of junk pages that you probably don't want to index.

``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_EXTRA_ARGS``

    This is a ``dict``. This dictionary is passed directly as keyword argument to the underlying ``LxmlLinkExtractor``
    class. For example, you could set this to ``{"restrict_xpaths": "..."}`` to restrict link extraction to certain
    parts of the page. See all the arguments you can pass in `Scrapy's LxmlLinkExtractor docs <https://docs.scrapy.org/en/latest/topics/link-extractors.html#module-scrapy.linkextractors.lxmlhtml>`_.
    You should not use the keys ``allow`` and ``deny`` in this setting, as they will ignored. Please use
    ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW`` or ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY`` for that.

Since ``WebSpider`` inherits from Scrapy's ``CrawlSpider``, you can also use any general Scrapy settings to control
many aspects of your crawl. For example, setting ``AUTOTHROTTLE_ENABLED=True`` will ensure you are not hitting the
website too hard. Setting ``DEPTH_LIMIT=2`` will ensure that only pages that can be reached after max 2 clicks from
the start URLs will be visited. You can see all the general settings available in
`Scrapy's built-in settings reference <https://docs.scrapy.org/en/latest/topics/settings.html#built-in-settings-reference>`_.

You can put your settings at the end of the ``settings.py`` file in the Scrapy project.

Here is an example settings for the ``WebSpider`` for crawling the Python documentation.

.. code-block:: python

    LANGSEARCH_WEB_SPIDER_START_URLS = ["https://docs.python.org/3/"]
    # Crawl only the latest version of docs, which is under /3/. We don't want links that start with /3.8/ or /3.9/
    LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = ["^https?://docs\.python\.org/3/"]
    LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY = [
        "/genindex",  # Don't crawl pages that primarily contain links e.g. https://docs.python.org/3/genindex-all.html
                      # or https://docs.python.org/3/genindex-A.html
        "/whatsnew",  # Don't crawl pages related to version info e.g. https://docs.python.org/3/whatsnew/3.8.html
        "docs\.python\.org/3//contents.html",  # This is like a table of contents
        "docs\.python\.org/3/c-api",  # Don't crawl pages about low level C API
        "docs\.python\.org/3/extending"  # Don't crawl pages about low level C API
    ]

.. _running:

Running the crawler
^^^^^^^^^^^^^^^^^^^

You can run the crawler by using the following command from anywhere inside the Scrapy project.

.. code-block:: console

    scrapy crawl <name_of_your_crawler>

Here, the name of your crawler should be the value of the ``name`` attribute of the crawler class you want to run. So, for
the example above, the command should be:

.. code-block:: console

    scrapy crawl my_crawler

The default log level for this command is ``DEBUG``, and this can lead to very busy output. You can change the log level
with the ``-L`` flag as shown below.

.. code-block:: console

    scrapy crawl my_crawler -L INFO

You can see all available flags in the `Scrapy documentation on the scrapy crawl command <https://docs.scrapy.org/en/latest/topics/commands.html#crawl>`_.

.. _dryrun:

Checking crawl behavior using the ``DryRunPipeline``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After writing the settings, you may want to check that the settings are actually doing what they are supposed to. For
this, you can use the ``DryRunPipeline`` which just prints out the URLs of the crawled pages to a file.

To activate the ``DryRunPipeline``, you need to add the following code to the ``settings.py`` file.

.. code-block:: python

    from langsearch.pipelines import DryRunPipeline

    ITEM_PIPELINES = {DryRunPipeline: 100}


The ``ITEM_PIPELINES`` Scrapy setting determines the pipeline components that will process each crawled item. Each pipeline
component is a class with a priority number e.g. ``DryRunPipeline: 100``. Pipeline component are then applied in the
order of their priorities, with each pipeline component acting on the result of the previous pipeline component.

In the above example, there is only one component ``DryRunPipeline``. So this is the only component that will process
the crawled pages.

The ``DryRunPipeline`` creates a file called ``dry_run_results.txt`` in the same directory where the ``scrapy crawl``
command was run. This file will contain the URLs of crawled items, one URL per line.

You can change the filepath that ``DryRunPipeline`` writes to using the ``LANGSEARCH_DRY_RUN_PIPELINE_FILEPATH`` setting,
as shown below.

.. code-block:: python

    LANGSEARCH_DRY_RUN_PIPELINE_FILEPATH = "link_list.txt"

Absolute paths are also supported.

When using the ``DryRunPipeline``, you may not want to run the full crawl, but rather restrict the crawl to the first N
pages. In that case, you can use the Scrapy setting ``CLOSESPIDER_PAGECOUNT``.

For example, you can use the following.

.. code-block:: python

    CLOSESPIDER_PAGECOUNT = 100

The crawler will then stop crawling after it has visited 100 pages.

What does ``WebSpider`` send to the item pipeline?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For each crawled page, the ``WebSpider`` generates a ``dict`` which is sent to the item pipeline. This ``dict`` is called
an **item**. The item produced by the ``WebSpider`` class contains only one key, called ``response``. The value is the
`Scrapy Response object <https://docs.scrapy.org/en/latest/topics/request-response.html#response-objects>`_ that was
obtained when downloading the content of a URL.

If you want to write your own crawler class but use LangSearch's built-in pipelines, your crawler should return
items which contain the Scrapy ``Response`` object in the key ``response``.

Restricting the crawl to a particular domain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You may want to restrict your crawl to a particular domain. There are many ways to do that.

The easiest way to do this is to add a class attribute ``allowed_domains`` to your crawler.

.. code-block:: python

    from langsearch.spiders import WebSpider

    class Crawler(WebSpider):
        name = "my_crawler"
        allowed_domains = ["docs.python.org"]   # Write just the domain, without scheme. Doesn't need to be a regex.

The ``allowed_domains`` attribute is implemented in Scrapy's ``CrawlSpider`` class, which is the parent class of
``WebSpider``.

The actual filtering is done in a spider middleware called `OffsiteMiddleware <https://docs.scrapy.org/en/latest/topics/spider-middleware.html#module-scrapy.spidermiddlewares.offsite>`_
which is `activated by default in any Scrapy project <https://docs.scrapy.org/en/latest/topics/settings.html#std-setting-SPIDER_MIDDLEWARES_BASE>`_.
The middleware reads the crawler's ``allowed_domains`` attribute and filters based on that.

Middlewares are classes that are applied in various phases of the request response cycle. To see how Scrapy uses
middlewares, please refer to `Scrapy's architecture documentation <https://docs.scrapy.org/en/latest/topics/architecture.html>`_.

An alternate way to prevent extracting out-of-domain links is to use the ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW``
settings.

.. code-block:: python

    LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = ["^https?://docs\.python\.org"]

This will prevent the crawler from extracting any link that doesn't start with `<http://docs.python.org>`_ or
`<https://docs.python.org>`_.

However, both these methods apply their filtering to links *before redirection*. If a link seems to be
in-domain, but actually redirects to an out-of-domain website, then those links will be let through. Sometimes, you may
want to write a filter for links *after redirection*. You can use the ``RegexFilterMiddleware`` class for that.

The ``RegexFilterMiddleware`` is a spider middleware that is applied after a response is downloaded for a crawled page,
after following all redirection. It filters out responses depending on the ``LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW`` and
``LANGSEARCH_REGEX_FILTER_MIDDLEWARE_DENY`` settings. Responses that are filtered out will not be processed further.
This means links will not be extracted from the response. The response will also not be sent to the item pipelines.

``LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW``

    This is a ``list`` of regular expressions. Responses will be allowed through only if the final URL
    (after redirection and without the scheme) matches any of the entries in this list.

``LANGSEARCH_REGEX_FILTER_MIDDLEWARE_DENY``

    This is a ``list`` of regular expressions. Responses will not be allowed through if the final URL
    (after redirection and without the scheme) matches any of the entries in this list. This has precedence over
    ``LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW``.

To use the ``RegexFilterMiddleware``, we need to turn off the ``OffsiteMiddleware`` and put the ``RegexFilterMiddleware``
in its place. Here's how you can do that.

.. code-block:: python

    SPIDER_MIDDLEWARES = {
        'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,   # Disable scrapy's OffsiteMiddleware
        'langsearch.middlewares.spidermiddlewares.RegexFilterMiddleware': 500,
    }

    LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW = ["^docs\.python\.org"]

Normally, it also makes sense to duplicate everything in ``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW`` and
``LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY`` in the ``RegexFilterMiddleware`` settings to ensure that you don't index
unwanted URLs due to a redirection.

This leads to a final settings that look like this:

.. code-block:: python

    LANGSEARCH_WEB_SPIDER_START_URLS = ["https://docs.python.org/3/"]
    # Crawl only the latest version of docs, which is under /3/. We don't want links that start with /3.8/ or /3.9/
    LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW = ["^https?://docs\.python\.org/3/"]
    LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY = [
        "/genindex",  # Don't crawl pages that primarily contain links e.g. https://docs.python.org/3/genindex-all.html
                      # or https://docs.python.org/3/genindex-A.html
        "/whatsnew",  # Don't crawl pages related to version info e.g. https://docs.python.org/3/whatsnew/3.8.html
        "docs\.python\.org/3//contents.html",  # This is like a table of contents
        "docs\.python\.org/3/c-api",  # Don't crawl pages about low level C API
        "docs\.python\.org/3/extending"  # Don't crawl pages about low level C API
    ]

    SPIDER_MIDDLEWARES = {
        'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,   # Disable scrapy's OffsiteMiddleware
        'langsearch.middlewares.spidermiddlewares.RegexFilterMiddleware': 500,
    }

    LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW = ["^docs\.python\.org/3/"]
    LANGSEARCH_REGEX_FILTER_MIDDLEWARE_DENY = [
        "/genindex",
        "/whatsnew",
        "docs\.python\.org/3//contents.html",
        "docs\.python\.org/3/c-api",
        "docs\.python\.org/3/extending"
    ]

.. _file:

Gathering data from local filesystem
------------------------------------

LangSearch gives you a way to collect selected files in the local filesystem using code that's very similar to the web
crawling case.

The collected files are then sent to the item pipeline (e.g. for indexing).

Just like the web crawling case, we will start by creating a file ``crawler.py`` under the ``spiders`` folder, and
write a crawler class in ``crawler.py``. But this time, we need to derive the crawler from the ``FileSpider`` class
instead of the ``WebSpider`` class.

.. code-block:: python

    from langchain.spiders import FileSpider

    class Crawler(FileSpider):
        name = "my_crawler"

That's all the code you need. The rest is controlled using the following settings which you put in ``settings.py``.

``LANGSEARCH_FILE_SPIDER_START_FOLDERS``

    This is list of folder paths (absolute paths). LangSearch will collect files under these paths. This setting is
    required.

``LANGSEARCH_FILE_SPIDER_FOLLOW_SUBFOLDERS``

    This is a ``bool``. If set to ``True``, the whole tree under each start folder will be collected.
    If set to ``False``, only files directly under each start folder will be collected.

    The default value is ``False``.

``LANGSEARCH_FILE_SPIDER_FOLLOW_SYMLINKS``

    This is a ``bool`` determining if symbolic links should be followed during file discovery. Setting this to ``True``
    might lead to files that are not under the start folder(s) to be collected (if the symbolic link points outside the
    tree under the start folder(s).

    The default value is ``False``.

``LANGSEARCH_FILE_SPIDER_ALLOW``

    This is a ``list`` of regular expressions. Only files with absolute paths matching any of the regular expressions
    will be  collected. If ``LANGSEARCH_FILE_SPIDER_FOLLOW_SYMLINKS`` is ``True``, the matching is done
    against the resolved absolute path.

    The default behavior is to allow everything.

``LANGSEARCH_FILE_SPIDER_DENY``

    This is a ``list`` of regular expressions. Files with absolute paths matching any of the regular expressions
    will not be collected. If ``LANGSEARCH_FILE_SPIDER_FOLLOW_SYMLINKS`` is ``True``, the matching is done
    against the resolved absolute path. This setting has precedence over ``LANGSEARCH_FILE_SPIDER_ALLOW``.

    The default behavior is to deny nothing.

Here is an example setting for indexing all the Python files under a Python project.

.. code-block:: python

    LANGSEARCH_FILE_SPIDER_START_FOLDERS = ["/home/user1/python-projects/project1"]
    LANGSEARCH_FILE_SPIDER_FOLLOW_SUBFOLDERS = True
    LANGSEARCH_FILE_SPIDER_ALLOW = ["\.py$"]

You can use the :ref:`DryRunPipeline to check if the correct files will be indexed <dryrun>`. See :ref:`running` to
see how to start the file collection.

For each collected file, the ``FileSpider`` class creates a ``dict``, which is called an **item** in Scrapy parlance.
This item to sent to the item pipeline for further processing (text extraction, indexing etc.).

The item created by the ``FileSpider`` has a single key called ``response``. This key holds the
`Scrapy Response object <https://docs.scrapy.org/en/latest/topics/request-response.html#response-objects>`_ that was
obtained when fetching the file via it's URL (all local files have a URL that starts with ``file://``).
