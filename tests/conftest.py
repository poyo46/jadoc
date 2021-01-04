from pathlib import Path

import pytest
from youcab import config, youcab


@pytest.fixture(scope="session")
def root_dir():
    return Path(__file__).parents[1].resolve()


@pytest.fixture(scope="session")
def tokenizers():
    tokenize_functions = []
    for dicdir in config.get_dicdirs():
        tokenize_functions.append(youcab.generate_tokenizer(dicdir=dicdir))
    return tokenize_functions
