import confuse, os,re, logging

from typing import Optional
from confuse import RootView
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Configuration:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir
        self._confuse: Optional[RootView] = None
        self.yaml_loader = confuse.yaml_util.Loader
        self.env_pattern = re.compile(r".*?\${(.*?)}")
        self.yaml_loader.add_implicit_resolver("!pathex", self.env_pattern ,None)
        self.yaml_loader.add_constructor("!pathex", self.env_constructor)

    def env_constructor(self, loader, node):
        value = loader.construct_scalar(node)
        for group in self.env_pattern.findall(value):
            if env := os.getenv(group):
                value = value.replace(f"${{{group}}}", env)
            else:
                logger.warning(f"Environment variable {group} not found")
        return value

    def load_config(self, env_path:str = None ):
        """
        Load all the configuration files witch remain within the config_dir

        :param env_path: Optionally specify the path to a .env file
        """
        load_dotenv(env_path)
        sources = [confuse.YamlSource(os.path.join(self.config_dir, file))
                   for file in os.listdir(self.config_dir) if file.endswith((".yaml", ".yml"))]
        self._confuse = confuse.RootView(sources)

    def __getitem__(self, item):
        assert self._confuse, "Make sure to call load_config before accessing the configuration"
        return self._confuse[item]
