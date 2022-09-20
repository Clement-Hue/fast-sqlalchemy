class LocalNotFound(Exception):
    def __init__(self, local):
        super().__init__(f"The local {local} is missing")


class PydanticI18n:
    def __init__(self, translations: dict, local):
        self.local = local
        self._translations = translations

    def translate(self, errors):
        return [{
            **error, "msg": self._translate(error.get("type"), error.get("ctx")) or error.get("msg")
        } for error in errors
        ]

    def _translate(self, err_type: str, ctx: dict):
        local_trans = self._translations.get(self.local, None)
        if local_trans is None:
            raise LocalNotFound(self.local)
        translated_msg: str = local_trans.get(err_type, None)
        if translated_msg is None:
            return None
        return translated_msg.format(*ctx.values())
