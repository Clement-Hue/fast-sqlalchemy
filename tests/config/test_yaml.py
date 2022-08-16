import os
from pathlib import Path

import pytest

from fast_sqlalchemy.config.yaml import Configuration
from dotenv import load_dotenv

root_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def config_test():
    return Configuration(os.path.join(root_dir, "test_cfg_dir"))


def test_get_yaml_config(config_test):
    config_test.load_config()
    assert config_test["db"] == "test_db"


def test_yaml_config_with_env(config_test):
    config_test.load_config(os.path.join(root_dir, ".env"))
    assert config_test["env_key"] == "var_foo.bar"


def test_multiple_files(config_test):
    config_test.load_config(os.path.join(root_dir, ".env"))
    assert config_test["other_file"]["key"] == "other"
    assert config_test["db"] == "test_db"


def test_get_all_config(config_test):
    config_test.load_config(os.path.join(root_dir, ".env"))
    assert config_test.get() == {'db': 'test_db',
                                 'env_key': 'var_foo.bar',
                                 'nested': {'key': {'subkey1': 'val1', 'subkey2': 'val2'}},
                                 'other_file': {'key': 'other'}}


def test_merge_test_config():
    config_test = Configuration(os.path.join(root_dir, "test_cfg_dir"),
                                test_config_dir=os.path.join(root_dir, "test_cfg_dir/tests"))
    config_test.load_config(use_test_config=True)
    assert config_test["nested"]["key"]["subkey2"] == "override"
    assert config_test["nested"]["key"] == {"subkey1": "val1", "subkey2": "override"}


def test_merge_config_empty_folder():
    config_test = Configuration(os.path.join(root_dir, "test_cfg_dir"),
                                test_config_dir=os.path.join(root_dir, "test_cfg_dir/empty"))
    config_test.load_config(use_test_config=True)
    assert config_test["nested"]["key"] == {"subkey1": "val1", "subkey2": "val2"}
