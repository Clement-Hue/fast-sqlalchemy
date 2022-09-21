import shutil, os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class GenerateProject:
    def __init__(self, name: str):
        self.name = name

    def generate(self):
        shutil.copytree(src=os.path.join(ROOT_DIR, "boilerplate"), dst=f"./{self.name}")