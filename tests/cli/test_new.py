import pytest

from fast_sqlalchemy.cli.commands import GenerateProject


def test_name_identifier():
    with pytest.raises(ValueError):
        GenerateProject("L@rem!")
