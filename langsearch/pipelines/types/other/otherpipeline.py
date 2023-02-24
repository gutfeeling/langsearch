from langsearch.pipelines.common.index import SimpleIndexPipeline
from langsearch.pipelines.common.storeitem import StoreItemPipeline
from langsearch.pipelines.common.python_readability import PythonReadabilityPipeline
from langsearch.pipelines.common.inscriptis import InscriptisPipeline
from langsearch.pipelines.common.textsplitter import TextSplitterPipeline
from langsearch.pipelines.common.tika import TikaPipeline
from langsearch.pipelines.types.enumerations import ItemType


class OtherPipeline:
    ITEM_TYPE = ItemType.OTHER

    ITEM_PIPELINES = {
        TikaPipeline: 400,
        PythonReadabilityPipeline: 410,
        InscriptisPipeline: 420,
        TextSplitterPipeline: 430,
        StoreItemPipeline: 440,
        SimpleIndexPipeline: 450
    }

    TIKA_PIPELINE_INPUTS = {
        "body": lambda item: getattr(item["response"], "body"),
        "url": lambda item: getattr(item["response"], "url")
    }

    PYTHON_READABILITY_PIPELINE_INPUTS = {
        "html": TikaPipeline.XML_OUTPUT,
        "url": lambda item: getattr(item["response"], "url")
    }

    INSCRIPTIS_PIPELINE_INPUTS = {
        "html": PythonReadabilityPipeline.HTML_WITHOUT_BP,
        "url": lambda item: getattr(item["response"], "url")
    }

    TEXT_SPLITTER_PIPELINE_INPUTS = {
        "text": InscriptisPipeline.EXTRACTED_TEXT,
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
        TikaPipeline: TIKA_PIPELINE_INPUTS,
        PythonReadabilityPipeline: PYTHON_READABILITY_PIPELINE_INPUTS,
        InscriptisPipeline: INSCRIPTIS_PIPELINE_INPUTS,
        TextSplitterPipeline: TEXT_SPLITTER_PIPELINE_INPUTS,
        StoreItemPipeline: STORE_ITEM_PIPELINE_INPUTS,
        SimpleIndexPipeline: SIMPLE_INDEX_PIPELINE_INPUTS
    }
