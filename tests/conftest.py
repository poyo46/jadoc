import os
from pathlib import Path

import pytest
from youcab import youcab


@pytest.fixture(scope="session")
def root_dir():
    return Path(__file__).parents[1].resolve()


@pytest.fixture(scope="session")
def tokenizers():
    dicdirs = os.getenv("MECAB_DICDIR")
    if dicdirs is None or dicdirs == "":
        raise ValueError(
            "Set the MeCab dicdir to be used for the test to the environment variable "
            + "``MECAB_DICDIR``, separated by a colon."
        )
    tokenize_functions = []
    for dicdir in dicdirs.split(":"):
        print("MECAB dicdir = " + dicdir)
        tokenize_functions.append(youcab.generate_tokenizer(dicdir=dicdir))
    return tokenize_functions
