from typing import Mapping


def deep_merge_dict(dict_1: dict, dict_2: dict):
    res = dict_1 | dict_2
    for key, value in dict_1.items():
        if isinstance(value, Mapping):
            res[key] = deep_merge_dict(dict_1[key], dict_2[key])
    return res
