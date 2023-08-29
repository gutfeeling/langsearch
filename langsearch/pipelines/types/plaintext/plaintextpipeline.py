from langsearch.pipelines.common.index import SimpleIndexPipeline
from langsearch.pipelines.common.storeitem import StoreItemPipeline
from langsearch.pipelines.common.textsplitter import TextSplitterPipeline
from langsearch.pipelines.common.inscriptis import InscriptisPipeline
from langsearch.pipelines.types.enumerations import ItemType


class GenericPlainTextPipeline:
    """
    Built-in pipelines should always use priorities between 400 and 600.
    """
    ITEM_TYPE = ItemType.TEXT

    ITEM_PIPELINES = {
        TextSplitterPipeline: 400,
        StoreItemPipeline: 410,
        SimpleIndexPipeline: 420
    }

    TEXT_SPLITTER_PIPELINE_INPUTS = {
        "text": lambda item: getattr(item["response"], "text"),
        "url": lambda item: getattr(item["response"], "url")
    }

    STORE_ITEM_PIPELINE_INPUTS = {
        "text": InscriptisPipeline.EXTRACTED_TEXT,
        "url": lambda item: getattr(item["response"], "url")
    }

    SIMPLE_INDEX_PIPELINE_INPUTS = {
        "sections": TextSplitterPipeline.SECTIONS,
        "url": lambda item: getattr(item["response"], "url"),
        "changed": StoreItemPipeline.CHANGED
    }

    PIPELINE_INPUTS = {
        TextSplitterPipeline: TEXT_SPLITTER_PIPELINE_INPUTS,
        StoreItemPipeline: STORE_ITEM_PIPELINE_INPUTS,
        SimpleIndexPipeline: SIMPLE_INDEX_PIPELINE_INPUTS
    }
