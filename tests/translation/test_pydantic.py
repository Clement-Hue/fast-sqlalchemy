import pytest

from fast_sqlalchemy.translation.pydantic import PydanticI18n, LocalNotFound


def test_translate_error():
    errors = [{'loc': ('body', 'firstname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.max_length', 'ctx': {'limit_value': 20}},
              {'loc': ('body', 'lastname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.min_length', 'ctx': {'limit_value': 10, "type": "string"}}]
    translations = {
        "fr_FR": {
            "value_error.any_str.max_length": "Ce champs doit faire {0} caractères",
            "value_error.any_str.min_length": "Ce {1} doit faire plus de {0} caractères",
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    res = py_18n.translate(errors)
    assert res[0]["msg"] == "Ce champs doit faire 20 caractères"
    assert res[1]["msg"] == "Ce string doit faire plus de 10 caractères"


def test_key_not_found():
    errors = [{'loc': ('body', 'firstname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.max_length', 'ctx': {'limit_value': 20}}]
    translations = {
        "fr_FR": {
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    res = py_18n.translate(errors)
    assert res[0]["msg"] == 'ensure this value has at most 20 characters'

def test_error_without_context():
    errors = [{'loc': ('body', 'firstname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.max_length', }]
    translations = {
        "fr_FR": {
            "value_error.any_str.max_length": "Ce champs est trop grand"
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    res = py_18n.translate(errors)
    assert res[0]["msg"] == "Ce champs est trop grand"

def test_local_missing():
    errors = [{'loc': ('body', 'firstname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.max_length', 'ctx': {'limit_value': 20}}]
    translations = {
        "fr": {
            "value_error.any_str.max_length": "Ce champs doit faire {0} caractères",
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    with pytest.raises(LocalNotFound):
        py_18n.translate(errors)

def test_get_locals():
    translations = {
        "fr_FR": {
        },
        "en_EN":{}
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    assert py_18n.locales == ("fr_FR", "en_EN")

def test_get_translations():
    translations = {
        "fr_FR": {
            "value_error.any_str.max_length": "Ce champs doit faire {0} caractères",
            "value_error.any_str.min_length": "Ce {1} doit faire plus de {0} caractères",
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    assert py_18n.get_translations("fr_FR") == translations["fr_FR"]

def test_key_as_dict():
    errors = [{'loc': ('body', 'firstname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.max_length', 'ctx': {'limit_value': 20}},
              {'loc': ('body', 'lastname'), 'msg': 'ensure this value has at most 20 characters',
               'type': 'value_error.any_str.min_length', 'ctx': {'limit_value': 10, "type": "string"}},
              {'loc': ('body', 'lastname'), 'msg': "other msg",
               'type': 'value_error.any_str.other'}
              ]
    translations = {
        "fr_FR": {
            "value_error": {
                "any_str.max_length": "Ce champs doit faire {0} caractères",
                "any_str": {
                    "min_length": "Ce {1} doit faire plus de {0} caractères",
                }
            }
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    res = py_18n.translate(errors)
    assert res[0]["msg"] == "Ce champs doit faire 20 caractères"
    assert res[1]["msg"] == "Ce string doit faire plus de 10 caractères"
    assert res[2]["msg"] == "other msg"

def test_simple_key_as_dict():
    errors = [{'loc': ('body', 'firstname'), 'msg': "simple msg", 'type': 'value_error'}]
    translations = {
        "fr_FR": {
            "value_error": {}
        }
    }
    py_18n = PydanticI18n(translations=translations, local="fr_FR")
    res = py_18n.translate(errors)
    assert res[0]["msg"] == "simple msg"
