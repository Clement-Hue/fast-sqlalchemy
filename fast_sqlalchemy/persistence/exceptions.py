
class AlreadyExistSession(RuntimeError):
    def __init__(self):
        super().__init__("A sqlalchemy session already exists in this context")