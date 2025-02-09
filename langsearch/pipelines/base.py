import importlib
import json
import logging
from pathlib import Path
import re

from langsearch.exceptions import SettingsError


logger = logging.getLogger(__name__)


# TODO: Use ItemAdapter in all pipelines
class BasePipeline:
    """
    INPUTS are used in child pipelines to declare the required item keys that pipeline needs
    Let's say a child pipeline declares
    ```
    INPUTS = {
        "html": "html",
        "url": "url"
    }
    ```
    This means that the child pipeline expects the `prepare_inputs(self, item)` method to set `self.html` and
    `self.url` to the correct item keys that contain this information for that ItemType.
    So this is done on a per-item basis.
    If a required instance variable is set to None by `prepare_inputs`, this means that the child pipeline doesn't need
    to operate on this ItemType and should just skip it.

    `prepare_inputs(self, item)` knows how to find the correct item keys for each ItemType because the orchestrating
    `assemble` function sets INPUTS for each pipeline, and it actually looks like this at runtime.
    ```
    INPUTS = {
        "html": {
            ItemType.HTML: FixHTMLPipeline.FIXED_HTML,
            ItemType.OTHER: TikaPipeline.XML_OUTPUT,
            # ... more item types
        }, # Sometimes, instead of using a dict, we use a callable. Use callable(item) to get the required key name.
        # Sometimes, we just use a value, meaning that all ItemTypes should use that value

        # ... other required instance variables
    }
    ```
    So the INPUTS that you see in the child pipeline definition is only an indication using defaults and a static item
    key (independent of ItemType). It will look different at runtime because it is dynamically modified by `assemble`
    before the scraping process launches.
    """
    INPUTS = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_setting_from_partial_key(cls, settings_obj, partial_key, default_class_var=None):
        if default_class_var is None:
            default_class_var = partial_key
        logger.info(f"Getting settings for partial key {partial_key} for class {cls}")
        for this_cls in cls.mro():
            key = f"LANGSEARCH_{this_cls.__name__.upper()}_{partial_key}"
            logger.debug(f"Trying environment variable {key}")
            value = settings_obj.get(key)
            if value is None:
                logger.debug(f"Trying class variable {default_class_var} of class {this_cls}")
                if hasattr(this_cls, default_class_var):
                    value = getattr(this_cls, default_class_var)
                    logger.info(f"Resolved partial key {partial_key} to class var {this_cls}.{default_class_var} "
                                f"with value {value}"
                                )
                    return value
            else:
                logger.info(f"Resolved partial key {partial_key} to env var {key} with value {value}")
                return value
        raise SettingsError(f"Failed to find value for setting with partial key {partial_key} for class {cls}")

    @staticmethod
    def get_from_dotted(dotted):
        parts = re.split(r"\.", dotted)
        module = importlib.import_module(".".join(parts[:-1]))
        return getattr(module, parts[-1])

    @staticmethod
    def get_params_from_file(filepath):
        path = Path(filepath)
        if not path.exists():
            raise SettingsError(f"Path {filepath} does not exist")
        if not path.is_file():
            raise SettingsError(f"Path {filepath} is not a file")
        with path.open("r") as f:
            params = json.load(f)
        return params

    def process_item(self, item, spider):
        self.prepare_inputs(item)
        item = self.apply(item, spider)
        return item

    def prepare_inputs(self, item):
        for argument, item_type_and_key in self.INPUTS.items():
            if not isinstance(item_type_and_key, dict):
                key = item_type_and_key
            else:
                try:
                    key = item_type_and_key[item["type"]]
                except KeyError:
                    setattr(self, argument, None)
                    continue
            if callable(key):
                try:
                    value = key(item)
                except:
                    setattr(self, argument, None)
                else:
                    setattr(self, argument, value)
                continue
            try:
                value = item[key]
            except KeyError:
                setattr(self, argument, None)
            else:
                setattr(self, argument, value)

    def apply(self, item, spider):
        """
        Should check if it has the right instance variables set to carry out the processing. Otherwise, DropItem.
        """
        raise NotImplementedError
