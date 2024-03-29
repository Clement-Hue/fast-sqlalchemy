import os, re, logging
from functools import reduce

import yaml
from dotenv import load_dotenv

from fast_sqlalchemy.config.exceptions import ConfigNotFound
from fast_sqlalchemy.config.utils import load_yaml_files, deep_merge_dict, parse_string

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
        self.env_pattern = re.compile(r".*?\${(.*?)}")
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
        loader.add_implicit_resolver("!pathex", self.env_pattern, None)
        loader.add_constructor("!pathex", self._env_constructor)
        return loader

    def _env_constructor(self, loader, node):
        value = loader.construct_scalar(node)
        for group in self.env_pattern.findall(value):
            split_group = group.split(":-",1)
            default_value = split_group[1] if len(split_group) == 2 else None
            if env := os.getenv(split_group[0]):
                value = value.replace(f"${{{group}}}", env)
            else:
                log_msg = f"Environment variable {split_group[0]} not found. "
                if default_value is not None:
                    value = value.replace(f"${{{group}}}", default_value)
                    log_msg += f"Using the default value: {default_value}"
                logger.warning(log_msg)
        return parse_string(value)

    def load_config(self, config: str = None):
        """
        Load all the configuration files within the config_dir

        :param config: Specify the configuration to use, the configuration must be a
            directory within the config directory witch contains yaml files that will be merged
            with the base configuration at the root of the config directory.
        """
        self._config = load_yaml_files(self.config_dir, self._yaml_loader)
        if config:
            self._load_specific_config(config)

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

    def _load_specific_config(self, specific_config: str):
        """
        Load a specific configuration based on the provided specific_config parameter and merge it with
        the base config.

        :param specific_config: The name of the specific configuration.
        """
        path = os.path.join(self.config_dir, specific_config)
        if not os.path.isdir(path):
            logger.warning(
                f"No directory with name '{specific_config}' find in the config "
                f"directory. Make sure to create a directory with name "
                f"'{specific_config}' within the config directory."
            )
            return
        self._config = deep_merge_dict(self._config, load_yaml_files(path, self._yaml_loader))
        logger.info(f"Configuration '{specific_config}' loaded")
