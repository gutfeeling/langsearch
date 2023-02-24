class DryRunPipeline:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = None

    @classmethod
    def from_crawler(cls, crawler):
        filepath = crawler.settings.get("LANGSEARCH_DRY_RUN_PIPELINE_FILEPATH", "dry_run_results.txt")
        return cls(filepath)

    def open_spider(self, spider):
        self.file = open(self.filepath, "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.file.write(f"{item['response'].url}\n")

