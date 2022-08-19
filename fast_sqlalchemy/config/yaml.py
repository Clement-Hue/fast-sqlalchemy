import os, re, logging
from functools import reduce

import yaml
from dotenv import load_dotenv

from fast_sqlalchemy.config.exceptions import ConfigNotFound
from fast_sqlalchemy.config.utils import load_yaml_files, deep_merge_dict

logger = logging.getLogger(__name__)


class Configuration:
    def __init__(self, config_dir=None, env_path=None):
        """
        Create a configuration object which load yaml files.

        :param config_dir: The directory which contains all the yaml files
        :param env_path: Optionally specify the path to a .env file
        """
        super().__init__()
        load_dotenv(env_path)
        self.__config = None
        self._yaml_loader = self._create_loader()
        self.config_dir = config_dir

    @property
    def _config(self):
        if self.__config is None:
            raise ConfigNotFound()
        return self.__config

    @_config.setter
    def _config(self, value):
        self.__config = value

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

    def load_config(self, config: str = None):
        """
        Load all the configuration files within the config_dir

        :param config: Specify the configuration to use, the configuration must be a
            directory within the config directory witch contains yaml files that will be merged
            with the base configuration at the root of the config directory.
        """
        self._config = load_yaml_files(self.config_dir, self._yaml_loader)
        if config:
            self._load_env_config(config)

    def __getitem__(self, item):
        try:
            return self._config[item]
        except KeyError:
            env_value = os.getenv(item)
            if env_value is None:
                raise
            logger.warning("Key {item} not found in yaml files. The environment variable is used as fallback")
            return os.getenv(item)


    def __setitem__(self, key, value):
        self._config[key] = value

    def get(self, key: str = None, default: any = None):
        """
        Return the configuration key's value in dot-separated notation. If no key is specified,
        it returns the entire configuration.
        A default value can be specified if the key is not found

        :param key: The key in dot-separated notation ex: 'database.host'
        :param default: A default value if key is not found
        :return: The configuration key's value or the entire configuration if no key is specified
        """
        try:
            if key is None:
                return self._config
            return reduce(lambda c, k: c[k], key.split("."), self)
        except KeyError:
            if default is None:
                raise
            return default

    def set(self, key: str, value: any):
        """
        Set a value to a key in dot-separated notation

        :param key: The key in dot-separated-notation ex: 'database.host'
        :param value: The value to set to the key
        """
        keys = key.split(".")
        obj = self._config
        for k in keys[:-1]:
            obj = obj.setdefault(k, {})
        obj[keys[-1]] = value

    def _load_env_config(self, env: str):
        path = os.path.join(self.config_dir, env)
        if not os.path.isdir(path):
            logger.warning(
                f"No directory with name '{env}' find in the config "
                f"directory. Make sure to create a directory with name "
                f"'{env}' within the config directory."
            )
            return
        test_config = load_yaml_files(path, self._yaml_loader)
        self._config = deep_merge_dict(self._config, test_config)
        logger.info(f"Configuration '{env}' loaded")
