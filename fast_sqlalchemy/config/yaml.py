import os, re, logging

import yaml
from dotenv import load_dotenv

from fast_sqlalchemy.config.utils import load_yaml_files, deep_merge_dict

logger = logging.getLogger(__name__)


class Configuration:
    def __init__(self, config_dir=None,  env_path=None):
        """
        Create a configuration object which load yaml files.

        :param config_dir: The directory which contains all the yaml files
        :param env_path: Optionally specify the path to a .env file
        """
        super().__init__()
        load_dotenv(env_path)
        self._config = None
        self._yaml_loader = self._create_loader()
        self.config_dir = config_dir

    def _create_loader(self):
        loader = yaml.Loader
        self.env_pattern = re.compile(r".*?\${(.*?)}")
        loader.add_implicit_resolver("!pathex", self.env_pattern, None)
        loader.add_constructor("!pathex", self._env_constructor)
        return loader

    def _env_constructor(self, loader, node):
        value = loader.construct_scalar(node)
        for group in self.env_pattern.findall(value):
            if env := os.getenv(group):
                value = value.replace(f"${{{group}}}", env)
            else:
                logger.warning(f"Environment variable {group} not found")
        return value
    def load_config(self, env: str=None):
        """
        Load all the configuration files within the config_dir

        :param env: Specify the environment to use, the environment configuration must
        be a directory within the config directory witch contains yaml files that  will override
        the configuration.
        """
        self._config = load_yaml_files(self.config_dir, self._yaml_loader)
        if env:
            self._load_env_config(env)

    def __getitem__(self, item):
        assert self._config, "Make sure to call load_config before accessing the configuration"
        return self._config[item]

    def __setitem__(self, key, value):
        assert self._config, "Make sure to call load_config before overriding the configuration"
        self._config[key] = value

    def get(self):
        return self._config

    def _load_env_config(self, env: str):
        path = os.path.join(self.config_dir, env)
        assert os.path.isdir(path), f"No directory with name '{env}' find in the config " \
                                    f"directory. Make sure to create a directory with name " \
                                    f"'{env}' within the config directory."
        test_config = load_yaml_files(path, self._yaml_loader)
        self._config = deep_merge_dict(self._config, test_config)
        logger.info(f"Configuration '{env}' loaded")
