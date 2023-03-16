import re

import tiktoken


def get_regex_from_list(list_to_convert):
    """
    This function will take a list of strings and convert it to a compiled regex.
    :param list_to_convert: A list of regex.
    :return: A compiled regex
    """
    if len(list_to_convert) == 0:
        raise ValueError("List to convert is empty")
    return re.compile(f"({'|'.join(list_to_convert)})")


def openai_length_function(text):
    """
    This function will take a string and return the length of the string as if it were encoded by openai.
    :param text: A string.
    :return: The length of the string as if it were encoded by openai.
    """
    return len(tiktoken.get_encoding("gpt2").encode(text))



