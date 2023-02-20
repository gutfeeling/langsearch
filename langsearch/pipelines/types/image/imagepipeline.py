from langsearch.pipelines.common.storeitem import StoreItemPipeline
from langsearch.pipelines.types.image.resize import ResizeImagePipeline
from langsearch.pipelines.types.image.imageindex import ImageIndexPipeline
from langsearch.pipelines.types.enumerations import ItemType


class ImagePipeline:
    """
    Built-in pipelines should always use priorities between 400 and 600.
    """
    ITEM_TYPE = ItemType.IMAGE

    ITEM_PIPELINES = {
        ResizeImagePipeline: 400,
        StoreItemPipeline: 410,
        ImageIndexPipeline: 420
    }

    RESIZE_IMAGE_PIPELINE_INPUTS = {
        "body": lambda item: getattr(item["response"], "body"),
        "url": lambda item: getattr(item["response"], "url")
    }

    STORE_ITEM_PIPELINE_INPUTS = {
        "url": lambda item: getattr(item["response"], "url")
    }

    IMAGE_INDEX_PIPELINE_INPUTS = {
        "body": ResizeImagePipeline.RESIZED_BYTES,
        "url": lambda item: getattr(item["response"], "url"),
        "changed": StoreItemPipeline.CHANGED
    }

    PIPELINE_INPUTS = {
        ResizeImagePipeline: RESIZE_IMAGE_PIPELINE_INPUTS,
        StoreItemPipeline: STORE_ITEM_PIPELINE_INPUTS,
        ImageIndexPipeline: IMAGE_INDEX_PIPELINE_INPUTS
    }
