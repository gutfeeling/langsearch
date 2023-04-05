import logging
from scrapy.http import Response
from scrapy.utils.httpobj import urlparse_cached

from langsearch.exceptions import IgnoreResponse
from langsearch.utils import get_regex_from_list

logger = logging.getLogger(__name__)


class RegexFilterMiddleware:
    def __init__(self, allow, deny, stats):
        self.allow = get_regex_from_list(allow) if len(allow) > 0 else None
        self.deny = get_regex_from_list(deny) if len(deny) > 0 else None
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        allow = crawler.settings.get("LANGSEARCH_REGEX_FILTER_MIDDLEWARE_ALLOW", ())
        deny = crawler.settings.get("LANGSEARCH_REGEX_FILTER_MIDDLEWARE_DENY", ())
        return cls(allow, deny, crawler.stats)

    def filtered(self, response):
        parsed = urlparse_cached(response)
        full_path = parsed.netloc + parsed._replace(scheme="", netloc="").geturl()
        if self.deny is not None and self.deny.search(full_path) is not None:
            return True
        if self.allow is not None and self.allow.search(full_path) is None:
            return True
        return False

    def process_spider_input(self, response, spider):
        if not isinstance(response, Response):
            return
        if self.filtered(response):
            message = f"{self.__class__.__name__} has filtered response with URL {response.url}"
            logger.debug(message)
            self.stats.inc_value(f"{self.__class__.__name__}/filtered")
            raise IgnoreResponse(message)

    # This seems to be called only on start_urls, because the requests from the CrawlSpider rule have an errback, which
    # is called instead
    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, IgnoreResponse):
            return []
