import confuse, os,re, logging

from typing import Optional
from confuse import RootView
from dotenv import load_dotenv

from fast_sqlalchemy.config.utils import deep_merge_dict

logger = logging.getLogger(__name__)

class Configuration:
    def __init__(self, config_dir=None, test_config_dir=None):
        self.config_dir = config_dir
        self._confuse: Optional[RootView] = None
        self.yaml_loader = confuse.yaml_util.Loader
        self.env_pattern = re.compile(r".*?\${(.*?)}")
        self.yaml_loader.add_implicit_resolver("!pathex", self.env_pattern ,None)
        self.yaml_loader.add_constructor("!pathex", self.env_constructor)
        self.test_config_dir = test_config_dir

    def env_constructor(self, loader, node):
        value = loader.construct_scalar(node)
        for group in self.env_pattern.findall(value):
            if env := os.getenv(group):
                value = value.replace(f"${{{group}}}", env)
            else:
                logger.warning(f"Environment variable {group} not found")
        return value

    def _override_with_test_config(self):
        assert self.test_config_dir, "You must specify a test directory if you use the flag "  \
                                     "'use_test_config'"
        sources = [confuse.YamlSource(os.path.join(self.test_config_dir, file))
                   for file in os.listdir(self.test_config_dir) if file.endswith((".yaml", ".yml"))]
        test_confuse = confuse.RootView(sources)
        self._confuse.set(deep_merge_dict(self._confuse.get(), test_confuse.get()))

    def load_config(self, env_path:str = None, use_test_config=False ):
        """
        Load all the configuration files witch remain within the config_dir

        :param env_path: Optionally specify the path to a .env file
        """
        load_dotenv(env_path)
        sources = [confuse.YamlSource(os.path.join(self.config_dir, file))
                   for file in os.listdir(self.config_dir) if file.endswith((".yaml", ".yml"))]
        self._confuse = confuse.RootView(sources)
        if use_test_config:
            self._override_with_test_config()

    def __getitem__(self, item):
        assert self._confuse, "Make sure to call load_config before accessing the configuration"
        return self._confuse[item]

