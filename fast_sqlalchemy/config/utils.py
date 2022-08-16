import os, yaml
from typing import Mapping, Type

from yaml import Loader


def load_yaml_files(directory: str, loader: Type[Loader]):
    data = {}
    for filename in os.listdir(directory):
        if filename.endswith((".yaml", ".yml")):
            with open(os.path.join(directory, filename)) as file:
                if loaded_data := yaml.load(file, Loader=loader):
                    data.update(loaded_data)
    return data


def deep_merge_dict(dict_1: dict, dict_2: dict):
    res = {**dict_1, **dict_2}
    for key, value in dict_1.items():
        if isinstance(value, Mapping) and key in dict_2:
            res[key] = deep_merge_dict(dict_1[key], dict_2[key])
    return res
