
class ConfigNotFound(Exception):
    def __init__(self):
        super().__init__("Configuration not found. Make sure to call load_config() before accessing or "
                         "overriding the configuration")