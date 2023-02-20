from io import BytesIO
import logging

from PIL import Image
from scrapy.exceptions import DropItem

from langsearch.exceptions import SettingsError
from langsearch.pipelines.base import BasePipeline


logger = logging.getLogger(__name__)


class ResizeImagePipeline(BasePipeline):
    INPUTS = {
        "body": "body",
        "url": "url",
    }
    RESIZED_BYTES = "resize_image_pipeline_resized_bytes"
    SCALE = 1
    RESIZE_ARGUMENTS = {}

    def __init__(self, scale, resized_width, resize_arguments, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = scale
        self.resized_width = resized_width
        self.resize_arguments = resize_arguments

    @classmethod
    def from_crawler(cls, crawler):
        scale = cls.get_setting_from_partial_key(crawler.settings, "SCALE")
        try:
            resized_width = cls.get_setting_from_partial_key(crawler.settings, "RESIZED_WIDTH")
        except SettingsError:
            resized_width = None
        resize_arguments = cls.get_setting_from_partial_key(crawler.settings, "RESIZE_ARGUMENTS")
        return cls(scale, resized_width, resize_arguments)

    def get_resized_size(self, original_size):
        if self.resized_width is not None:
            return self.resized_width, int(self.resized_width * original_size[1] / original_size[0])
        else:
            return tuple(int(x * self.scale) for x in original_size)

    def apply(self, item, spider):
        if not hasattr(self, "body") or self.body is None:
            return item
        if not hasattr(self, "url"):
            return item
        try:
            with BytesIO(self.body) as original:
                im = Image.open(original)
                resized_size = self.get_resized_size(im.size)
                im = im.resize(resized_size, **self.resize_arguments)
                with BytesIO() as resized:
                    im.save(resized, format=im.format)
                    item[self.RESIZED_BYTES] = resized.getvalue()
            return item
        except:
            message = f"Pillow failed to resize image for url {self.url}"
            logger.exception(message)
            raise DropItem(message)
