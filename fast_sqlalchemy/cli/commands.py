import shutil, os
from secrets import token_hex

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class GenerateProject:
    def __init__(self, name: str):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.isidentifier():
            raise ValueError(f"{value} is a not a valid project name")
        self._name = value
    def generate(self):
        shutil.copytree(src=os.path.join(ROOT_DIR, "../../__template__"), dst=self.name)
        self._replace_placeholder()

    def _replace_placeholder(self):
        for subdir, dirs, files in os.walk(self.name):
            for file in files:
                with open(os.path.join(subdir, file), "r+") as template_file:
                    template = template_file.read()
                    template = template.replace("__template__", self.name)
                    template = template.format(PROJECT_NAME=self.name, SECRET_KEY=token_hex(32))
                    template_file.seek(0)
                    template_file.write(template)
                    template_file.truncate()

