import re


def get_regex_from_list(list_to_convert):
    """
    This function will take a list of strings and convert it to a compiled regex.
    :param list_to_convert: A list of regex.
    :return: A compiled regex
    """
    if len(list_to_convert) == 0:
        raise ValueError("List to convert is empty")
    return re.compile(f"({'|'.join(list_to_convert)})")



