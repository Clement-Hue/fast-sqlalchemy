import logging
from copy import copy

class ColorFormatter(logging.Formatter):
    green = "\x1b[0;32m"
    default = "\x1b[0m"
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    cyan = '\x1b[38;5;37m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'


    def __init__(self, datefmt=None):
        super().__init__(fmt= f"{self.green} %(asctime)s {self.default} - %(levelname)s {self.cyan}  %(name)s %(funcName)s() "
                              f"L%(lineno)-4d {self.default} %(message)s",
                         datefmt=datefmt)
        self.FORMATS = {
            logging.DEBUG: self.grey,
            logging.INFO: self.blue,
            logging.WARNING: self.yellow,
            logging.ERROR: self.red,
            logging.CRITICAL: self.bold_red
        }

    def format(self, record):
        colored_record = copy(record)
        level_color = self.FORMATS.get(colored_record.levelno)
        colored_record.levelname = f"{level_color} {colored_record.levelname}{self.default}"
        return super().format(colored_record)
