import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from langsearch.exceptions import SettingsError


class WebSpider(CrawlSpider):
    name = "langsearch_webspider"

    def __init__(self, start_urls, link_extractor_allow, link_extractor_deny, link_extractor_extra_args,
                 *args, **kwargs
                 ):
        if not hasattr(self, "start_urls") and start_urls is not None:
            self.start_urls = start_urls
        if len(link_extractor_allow) > 0 or len(link_extractor_deny) > 0:
            self.rules += (self.get_rule(link_extractor_allow, link_extractor_deny, link_extractor_extra_args),)
        super().__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        start_urls = crawler.settings.get("LANGSEARCH_WEB_SPIDER_START_URLS")
        if start_urls is not None and not isinstance(start_urls, (list, tuple)):
            raise SettingsError(
                f"setting LANGSEARCH_WEB_SPIDER_START_URLS must be a list or tuple, got {type(start_urls)}."
            )
        link_extractor_allow = crawler.settings.get("LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW", ())
        if not isinstance(link_extractor_allow, (list, tuple)):
            raise SettingsError(
                "setting LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_ALLOW must be a list or tuple, "
                f"got {type(link_extractor_allow)}"
            )

        link_extractor_deny = crawler.settings.get("LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY", ())
        if not isinstance(link_extractor_deny, (list, tuple)):
            raise SettingsError(
                "setting LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_DENY must be a list or tuple, "
                f"got {type(link_extractor_deny)}"
            )

        link_extractor_extra_args = crawler.settings.get("LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_EXTRA_ARGS", {})
        if not isinstance(link_extractor_extra_args, dict):
            raise SettingsError(
                "setting LANGSEARCH_WEB_SPIDER_LINK_EXTRACTOR_EXTRA_ARGS must be a dict, "
                f"got {type(link_extractor_extra_args)}"
            )

        spider = super().from_crawler(crawler, start_urls, link_extractor_allow, link_extractor_deny,
                                      link_extractor_extra_args, *args, **kwargs
                                      )
        return spider

    def get_rule(self, link_extractor_allow, link_extractor_deny, link_extractor_extra_args):
        link_extractor = LinkExtractor(
            **{**link_extractor_extra_args, "allow": link_extractor_allow, "deny": link_extractor_deny}
            )
        return Rule(link_extractor, callback=self.parse, follow=True)

    def parse(self, response, **kwargs):
        item = {"response": response}
        return item

    # Scrapy's CrawlSpider will call this parser for the start_urls
    def parse_start_url(self, response, **kwargs):
        return self.parse(response, **kwargs)

    # We use dont_filter=False option for start_urls. Otherwise, the dupefilter doesn't store the start_url, leading
    # to two allowed requests to the same url.
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url)
