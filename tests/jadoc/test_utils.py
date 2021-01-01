import os

import pytest

from jadoc.utils import ENV_DEBUG, debug_on


class TestUtils:
    def test_debug_mode_should_be_disabled_if_no_env(self):
        del os.environ[ENV_DEBUG]
        assert not debug_on()

    @pytest.mark.parametrize("env_value", ("true", "on"))
    def test_debug_mode_should_be_enabled(self, env_value):
        os.environ[ENV_DEBUG] = env_value
        assert debug_on()

    @pytest.mark.parametrize("env_value", ("false", "off"))
    def test_debug_mode_should_be_disabled(self, env_value):
        os.environ[ENV_DEBUG] = env_value
        assert not debug_on()
