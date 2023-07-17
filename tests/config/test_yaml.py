import os

import pytest

from fast_sqlalchemy.config.exceptions import ConfigNotFound
from fast_sqlalchemy.config.yaml import Configuration

root_dir = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def config_test():
    return Configuration(os.path.join(root_dir, "test_cfg_dir"),
                         env_path=os.path.join(root_dir, "env_test"))

def test_get_yaml_config(config_test):
    config_test.load_config()
    assert config_test["db"] == "test_db"


def test_yaml_config_with_env(config_test):
    config_test.load_config()
    assert config_test["env_key"] == "var_foo.bar"


def test_multiple_files(config_test):
    config_test.load_config()
    assert config_test["other_file"]["key"] == "other"
    assert config_test["db"] == "test_db"

def test_set_item(config_test):
    config_test.load_config()
    config_test["nested"]["key"]["subkey1"] = "override"
    assert config_test["nested"]["key"]["subkey1"] == "override"
    assert config_test["nested"]["key"]["subkey2"] == "val2"

def test_get_all_config(config_test):
    config_test.load_config()
    assert config_test.get() == {'db': 'test_db',
                                 "number": 587,
                                 "bool": True,
                                 'env_key': 'var_foo.bar',
                                 "env_default": "gg:-fo@gmail.com",
                                 "env_default_empty": "",
                                 'nested': {'key': {'subkey1': 'val1', 'subkey2': 'val2'}},
                                 'other_file': {'key': 'other'}}

def test_bool_and_number_value(config_test):
    config_test.load_config()
    assert config_test.get("number") == 587
    assert config_test.get("bool") is True
    assert config_test["bool"] is True
def test_merge_config(config_test):
    config_test.load_config(config="test")
    assert config_test["nested"]["key"]["subkey2"] == "override"
    assert config_test["nested"]["key"] == {"subkey1": "val1", "subkey2": "override"}


def test_merge_config_empty_directory(config_test):
    config_test.load_config(config="empty")
    assert config_test["nested"]["key"] == {"subkey1": "val1", "subkey2": "val2"}

def test_merge_config_not_found_directory(config_test, caplog):
    config_test.load_config(config="not_found")
    assert "No directory" in caplog.text


def test_fallback_to_env_if_key_not_found(config_test):
    config_test.load_config()
    assert config_test["env_var"] == "fallback"

def test_raise_exception_if_env_fallback_not_found(config_test):
    config_test.load_config()
    with pytest.raises(KeyError):
        val = config_test["not_exist"]

def test_get_env_with_dot_annotation(config_test):
    config_test.load_config()
    assert config_test.get("nested.key.subkey2") == "val2"
    assert config_test.get("nested.key.subkey100", "default") == "default"
    assert config_test.get("env_var") == "fallback"
    with pytest.raises(KeyError):
        config_test.get("nested.key.subkey100")

def test_set_env_with_dot_annotation(config_test):
    config_test.load_config()
    config_test.set("nested.key.subkey2", "override")
    config_test.set("new_nested.key.val", "new")
    config_test.set("db", "db_override")
    assert config_test.get("nested.key.subkey2") == "override"
    assert config_test.get("db") == "db_override"
    assert config_test.get("new_nested.key.val") == "new"

def test_access_config_without_load_config(config_test):
    with pytest.raises(ConfigNotFound):
        config_test.set("nested.key.subkey2", "override")
    with pytest.raises(ConfigNotFound):
        config_test.get("nested.key.subkey2")
    with pytest.raises(ConfigNotFound):
        val = config_test["nested.key"]["subkey2"]
    with pytest.raises(ConfigNotFound):
        config_test["nested.key"]["subkey2"] = "test"

def test_env_default_value(config_test):
    config_test.load_config()
    assert config_test["env_default"] == "gg:-fo@gmail.com"

def test_env_default_value_empty(config_test):
    config_test.load_config()
    assert config_test["env_default_empty"] == ""
