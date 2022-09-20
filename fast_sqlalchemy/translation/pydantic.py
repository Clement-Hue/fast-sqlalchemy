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

    def _translate(self, err_type: str, ctx: dict = None):
        translated_msg: str = self.get_translations(self.local).get(err_type, None)
        if translated_msg is None:
            return None
        return translated_msg.format(*ctx.values()) if ctx is not None else translated_msg

    @property
    def locales(self):
        return tuple(self._translations.keys())

    def get_translations(self, local: str):
        local_trans = self._translations.get(local, None)
        if local_trans is None:
            raise LocalNotFound(local)
        return local_trans
