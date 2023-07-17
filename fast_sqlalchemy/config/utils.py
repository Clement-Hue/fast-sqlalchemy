import os, yaml, re
from typing import Mapping, Type

from yaml import Loader


def load_yaml_files(directory: str, loader: Type[Loader]):
    """
    Load YAML files from the specified directory using the given loader.

    :param directory: The directory path where the YAML files are located.
    :param loader: The YAML loader class to use for parsing.
    :return: A dictionary containing the merged data from all the YAML files.
    """
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith((".yaml", ".yml")):
            with open(os.path.join(directory, filename)) as file:
                if loaded_data := yaml.load(file, Loader=loader):
                    data.update(loaded_data)
    return data


def deep_merge_dict(dict_1: dict, dict_2: dict):
    """
    Deep merge two dictionaries, recursively merging nested dictionaries.

    :param dict_1: The first dictionary to merge.
    :param dict_2: The second dictionary to merge.
    :return: A new dictionary containing the merged result.
    """
    res = {**dict_1, **dict_2}
    for key, value in dict_1.items():
        if isinstance(value, Mapping) and key in dict_2:
            res[key] = deep_merge_dict(dict_1[key], dict_2[key])
    return res

def parse_string(value):
    patterns = [
        (r'^\d+$', int),        # Integer pattern
        (r'^\d+\.\d+$', float),  # Float pattern
        (r'^(true|false)$', bool)  # Boolean pattern
    ]

    for pattern, data_type in patterns:
        if re.match(pattern, value, re.IGNORECASE):
            return data_type(value)
    return value