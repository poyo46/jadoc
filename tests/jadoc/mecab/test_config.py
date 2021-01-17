import pytest

from jadoc.errors import MecabConfigError
from jadoc.mecab.config import _mecab_config_dicdir, get_dicdirs


class TestMecabConfig:
    def test_should_return_a_directory_path(self):
        path = _mecab_config_dicdir(mecab_config="mecab-config")
        assert path.is_dir()

    def test_should_raise_an_error_when_the_executable_path_is_invalid(self):
        with pytest.raises(MecabConfigError):
            _mecab_config_dicdir(mecab_config="foobar")


def test_get_dicdirs():
    for dicdir in get_dicdirs():
        assert dicdir.is_dir()
