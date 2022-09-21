from typing import Optional


class LocalNotFound(Exception):
    def __init__(self, local):
        super().__init__(f"The local {local} is missing")


class PydanticI18n:
    def __init__(self, translations: dict, local):
        self.local = local
        self._translations = translations

    def translate(self, errors):
        return [{
            **error, "msg": self._translate(error.get("type", None), error.get("ctx", None)) or error.get("msg")
        } for error in errors
        ]

    def _translate(self, err_type: str, ctx: dict = None):
        source: dict = self.get_translations(self.local)
        translated_msg: Optional[str] = self._get_msg(key=err_type, source=source)
        if translated_msg is None:
            return None
        return translated_msg.format(*ctx.values()) if ctx is not None else translated_msg

    def _get_msg(self, key: str, source: dict = None):
        if source is None:
            return None
        if msg := source.get(key, None):
            return msg
        split_key = key.split(".")
        return self._get_msg(".".join(split_key[1:]) , source.get(split_key[0], None))

    @property
    def locales(self):
        return tuple(self._translations.keys())

    def get_translations(self, local: str):
        local_trans = self._translations.get(local, None)
        if local_trans is None:
            raise LocalNotFound(local)
        return local_trans
