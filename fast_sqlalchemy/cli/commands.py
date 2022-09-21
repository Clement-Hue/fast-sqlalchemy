import shutil, os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class GenerateProject:
    def __init__(self, name: str):
        self.name = name

    def generate(self):
        shutil.copytree(src=os.path.join(ROOT_DIR, "boilerplate"), dst=self.name)
        self._replace_placeholder()


    def _replace_placeholder(self):
        for subdir, dirs, files in os.walk(self.name):
            for file in files:
                with open(os.path.join(subdir, file), "r") as template_file:
                    template = template_file.read()
                with open(os.path.join(subdir, file), "w") as write_file:
                    write_file.write(template.format(PROJECT_NAME=self.name))