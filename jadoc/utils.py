import os

from . import __title__

ENV_DEBUG = f"{__title__.upper()}_DEBUG"


def debug_on() -> bool:
    """Whether debug mode is enabled or not.

    Returns
    -------
    bool
        True if debug mode is enabled, False otherwise.
    """
    env = os.getenv(ENV_DEBUG)
    if env is None:
        # default
        return False
    if env.lower().strip() in ("true", "on"):
        return True
    else:
        return False
