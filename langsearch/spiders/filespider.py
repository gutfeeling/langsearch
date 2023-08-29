from pathlib import Path

import scrapy
from scrapy.spiders import Spider

from langsearch.exceptions import SettingsError
from langsearch.utils import get_regex_from_list


class FileSpider(Spider):
    name = "langsearch_filespider"

    def __init__(self, start_folders, follow_subfolders, follow_symlinks, allow, deny, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_folders = []
        for folder in start_folders:
            folder = Path(folder)
            if not folder.is_absolute():
                raise SettingsError(f"folder {folder} is not an absolute path")
            if not folder.exists():
                raise SettingsError(f"folder {folder} does not exist")
            if not folder.is_dir():
                raise SettingsError(f"{folder} is not a folder")
            self.start_folders.append(folder)

        self.follow_subfolders = follow_subfolders
        self.follow_symlinks = follow_symlinks
        self.allow = get_regex_from_list(allow) if len(allow) > 0 else None
        self.deny = get_regex_from_list(deny) if len(deny) > 0 else None

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        start_folders = crawler.settings.get("LANGSEARCH_FILE_SPIDER_START_FOLDERS")
        if start_folders is None:
            raise SettingsError("setting LANGSEARCH_FILE_SPIDER_START_FOLDERS is missing")
        if not isinstance(start_folders, (list, tuple)):
            raise SettingsError(
                f"setting LANGSEARCH_FILESPIDER_START_FOLDERS must be a list or tuple, got {type(start_folders)}."
            )

        follow_subfolders = crawler.settings.get("LANGSEARCH_FILE_SPIDER_FOLLOW_SUBFOLDERS", False)
        if not isinstance(follow_subfolders, bool):
            raise SettingsError(
                f"setting LANGSEARCH_FILE_SPIDER_FOLLOW_SUBFOLDERS must be a boolean, got {type(follow_subfolders)}"
            )

        follow_symlinks = crawler.settings.get("LANGSEARCH_FILE_SPIDER_FOLLOW_SYMLINKS", False)
        if not isinstance(follow_symlinks, bool):
            raise SettingsError(
                f"setting LANGSEARCH_FILE_SPIDER_FOLLOW_SYMLINKS must be a boolean, got {type(follow_symlinks)}"
            )

        allow = crawler.settings.get("LANGSEARCH_FILE_SPIDER_ALLOW", ())
        if not isinstance(allow, (list, tuple)):
            raise SettingsError(f"setting LANGSEARCH_FILE_SPIDER_ALLOW must be a list or tuple, got {type(allow)}")

        deny = crawler.settings.get("LANGSEARCH_FILE_SPIDER_DENY", ())
        if not isinstance(allow, (list, tuple)):
            raise SettingsError(f"setting LANGSEARCH_FILE_SPIDER_DENY must be a list or tuple, got {type(deny)}")

        spider = super().from_crawler(crawler, start_folders, follow_subfolders, follow_symlinks, allow, deny,
                                      *args, **kwargs
                                      )
        return spider

    def filtered(self, path):
        if self.deny is not None and self.deny.search(str(path)) is not None:
            return True
        if self.allow is not None and self.allow.search(str(path)) is None:
            return True
        return False

    def get_files(self, folder):
        for child in folder.iterdir():
            if child.is_symlink():
                if self.follow_symlinks:
                    child = child.resolve()
                    if self.filtered(child):
                        continue
                else:
                    continue
            if child.is_dir():
                if self.follow_subfolders:
                    yield from self.get_files(child)
            elif not self.filtered(child):
                yield child

    def start_requests(self):
        for folder in self.start_folders:
            for file in self.get_files(folder):
                yield scrapy.Request(file.as_uri(), callback=self.parse)

    def parse(self, response, **kwargs):
        item = {"response": response}
        return item
