import confuse, os


class Configuration:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir
        self._confuse = None

    def load_config(self):
        sources = [confuse.YamlSource(os.path.join(self.config_dir, file))
                   for file in os.listdir(self.config_dir) if file.endswith((".yaml", ".yml"))]
        self._confuse = confuse.RootView(sources)

    def __getitem__(self, item):
        return self._confuse[item]
