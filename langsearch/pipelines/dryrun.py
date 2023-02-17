class DryRunPipeline:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    @classmethod
    def from_crawler(cls, crawler):
        filename = crawler.settings.get("LANGSEARCH_DRY_RUN_PIPELINE_FILENAME", "dry_run_results.txt")
        return cls(filename)

    def open_spider(self, spider):
        self.file = open(self.filename, "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.file.write(f"{item['response'].url}\n")

