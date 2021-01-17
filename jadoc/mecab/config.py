import subprocess
from pathlib import Path
from typing import List

from jadoc.errors import MecabConfigError


def _mecab_config_dicdir(mecab_config: str) -> Path:
    """Get the result of executing ``mecab-config --dicdir``.

    Parameters
    ----------
    mecab_config : str
        Executable path of mecab-config.

    Returns
    -------
    Path
        The path where MeCab dictionary directories are stored.
    """
    try:
        result = subprocess.run(
            [mecab_config, "--dicdir"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        path = result.stdout.decode("utf-8").splitlines()[0]
        return Path(path)
    except FileNotFoundError:
        raise MecabConfigError("`mecab-config` is not found.")


def get_dicdirs(mecab_config: str = "mecab-config") -> List[Path]:
    """Get MeCab dictionary directories.

    Parameters
    ----------
    mecab_config : str
        Executable path of mecab-config, by default "mecab-config".

    Returns
    -------
    List[Path]
        MeCab dictionary directories.
    """
    dicdirs = []
    for path in _mecab_config_dicdir(mecab_config).glob("**/dicrc"):
        dicdirs.append(path.parent.resolve())
    return dicdirs
