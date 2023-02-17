import os

from langchain.llms.loading import load_llm_from_config
import tiktoken

from langsearch.exceptions import SettingsError


class LLMMixin:
    SERIALIZED_LLM = {
        "_type": "openai",
        "temperature": 0
    }
    LENGTH_FUNCTION = lambda text: len(tiktoken.get_encoding("gpt2").encode(text))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        serialized_llm = self.__class__.get_setting_from_partial_key(os.environ, "SERIALIZED_LLM")
        if isinstance(serialized_llm, str):
            serialized_llm = self.load_params_from_file(serialized_llm)
        self.llm = load_llm_from_config(serialized_llm)
        length_function = self.__class__.get_setting_from_partial_key(os.environ, "LENGTH_FUNCTION")
        if isinstance(length_function, str):
            length_function = self.get_from_dotted(length_function)
        self.length_function = length_function
