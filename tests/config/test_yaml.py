import os
from fast_alchemy.config.yaml import Configuration


def test_get_yaml_config():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config = Configuration(os.path.join(root_dir, "test_cfg_dir"))
    config.load_config()
    assert config["db"].get() == "test"
