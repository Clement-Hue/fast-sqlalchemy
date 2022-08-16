import os, re, logging


import yaml
from dotenv import load_dotenv

from fast_sqlalchemy.config.utils import load_yaml_files, deep_merge_dict

logger = logging.getLogger(__name__)


class Configuration():
    def __init__(self, config_dir=None, test_config_dir=None):
        super().__init__()
        self._config = None
        self.config_dir = config_dir
        self.test_config_dir = test_config_dir
        self.yaml_loader = self._create_loader()

    def _create_loader(self):
        loader = yaml.Loader
        self.env_pattern = re.compile(r".*?\${(.*?)}")
        loader.add_implicit_resolver("!pathex", self.env_pattern, None)
        loader.add_constructor("!pathex", self.env_constructor)
        return loader

    def env_constructor(self, loader, node):
        value = loader.construct_scalar(node)
        for group in self.env_pattern.findall(value):
            if env := os.getenv(group):
                value = value.replace(f"${{{group}}}", env)
            else:
                logger.warning(f"Environment variable {group} not found")
        return value
    def load_config(self, env_path: str = None, use_test_config=False):
        """
        Load all the configuration files witch remain within the config_dir

        :param env_path: Optionally specify the path to a .env file
        """
        load_dotenv(env_path)
        self._config = load_yaml_files(self.config_dir, self.yaml_loader)
        if use_test_config:
            self._override_with_test_config()

    def __getitem__(self, item):
        assert self._config, "Make sure to call load_config before accessing the configuration"
        return self._config[item]

    def get(self):
        return self._config

    def _override_with_test_config(self):
        assert self.test_config_dir, "You must specify a test directory if you use the flag " \
                                     "'use_test_config'"
        test_config = load_yaml_files(self.test_config_dir, self.yaml_loader)
        self._config = deep_merge_dict(self._config, test_config)
