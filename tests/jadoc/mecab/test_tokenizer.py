from typing import Callable, List, Optional

import pytest

from jadoc.errors import InvalidTokenizerError, NotFoundNodeFormatError
from jadoc.mecab import tokenizer as MODULE_TO_BE_TESTED
from jadoc.mecab.config import get_dicdirs
from jadoc.mecab.tokenizer import (
    _find_index,
    _find_node_format,
    _mecab_tagger,
    check_tokenizer,
    generate_tokenizer,
)
from jadoc.word.pos import Noun
from jadoc.word.word import Word

dicdirs = [None] + get_dicdirs()


@pytest.mark.parametrize(
    "dicdir",
    dicdirs,
)
@pytest.mark.parametrize(
    "node_format",
    [None, r"%m\\n"],
)
@pytest.mark.parametrize(
    "unk_format",
    [None, r"%m\\n"],
)
def test__mecab_tagger(dicdir, node_format, unk_format):
    tokens = ["毎日", "とても", "歩き", "ます"]
    text = "".join(tokens)
    tagger = _mecab_tagger(
        dicdir=dicdir, node_format=node_format, unk_format=unk_format
    )
    result = tagger.parse(text)
    for token in tokens:
        assert token in result


@pytest.mark.parametrize(
    "items, equal_to, include, expect",
    [
        (["aaa", "bbb", "ccc"], "bbb", None, 1),
        (["aaa", "bbb", "ccc"], "cc", None, None),
        (["aaa", "bbb", "ccc"], "ddd", None, None),
        (["aaa", "bbb", "ccc"], None, "ccc", 2),
        (["aaa", "bbb", "ccc"], None, "cc", 2),
        (["aaa", "bbb", "ccc"], None, "ddd", None),
    ],
)
def test__find_index(items, equal_to, include, expect):
    assert _find_index(items, equal_to=equal_to, include=include) == expect


@pytest.mark.parametrize(
    "dicdir",
    dicdirs,
)
def test__find_node_format(dicdir):
    node_format = _find_node_format(dicdir=dicdir)
    assert len(node_format) > 0


def test__find_node_format_if_not_found(monkeypatch):
    def find_index(
        items: List[str], equal_to: Optional[str] = None, include: Optional[str] = None
    ):
        return None

    monkeypatch.setattr(MODULE_TO_BE_TESTED, "_find_index", find_index)
    with pytest.raises(NotFoundNodeFormatError):
        _find_node_format()


@pytest.mark.parametrize(
    "tokenize_function",
    [
        lambda x: [
            Word("楽しい", ["形容詞", "一般"], "楽しい", "形容詞", "連体形-一般"),
            Word("本", ["名詞", "普通名詞", "一般"]),
            Word("を", ["助詞", "格助詞"]),
            Word("よく", ["副詞"], "良く"),
            Word("読み", ["動詞", "一般"], "読む", "五段-マ行", "連用形-一般"),
            Word("ます", ["助動詞"], "ます", "助動詞-マス", "終止形-一般"),
        ]
    ],
)
def test_check_tokenizer_returns_none_if_valid(tokenize_function):
    assert check_tokenizer(tokenize_function) is None


@pytest.mark.parametrize(
    "tokenize_function",
    [
        lambda x: [],  # invalid length
        lambda x: [
            Word("楽しい", ["形容詞", "一般"], "楽しい", "形容詞", "連体形-一般"),
            Word("本", ["名詞", "普通名詞", "一般"]),
            Word("を", ["助詞", "格助詞"]),
            Word("良く", ["副詞"], "良く"),  # invalid surface
            Word("読み", ["動詞", "一般"], "読む", "五段-マ行", "連用形-一般"),
            Word("ます", ["助動詞"], "ます", "助動詞-マス", "終止形-一般"),
        ],
        lambda x: [
            Word("楽しい", ["形容詞", "一般"], "楽しい", "形容詞", "連体形-一般"),
            Word("本", ["foo"]),  # invalid pos
            Word("を", ["助詞", "格助詞"]),
            Word("よく", ["副詞"], "良く"),
            Word("読み", ["動詞", "一般"], "読む", "五段-マ行", "連用形-一般"),
            Word("ます", ["助動詞"], "ます", "助動詞-マス", "終止形-一般"),
        ],
        lambda x: [
            Word("楽しい", ["形容詞", "一般"], "楽しい", "形容詞", "連体形-一般"),
            Word("本", ["名詞", "普通名詞", "一般"]),
            Word("を", ["助詞", "格助詞"], c_type_info="五段活用"),  # invalid conjugation
            Word("よく", ["副詞"], "良く"),
            Word("読み", ["動詞", "一般"], "読む", "五段-マ行", "連用形-一般"),
            Word("ます", ["助動詞"], "ます", "助動詞-マス", "終止形-一般"),
        ],
    ],
)
def test_check_tokenizer_raises_error_if_invalid(tokenize_function):
    with pytest.raises(InvalidTokenizerError):
        check_tokenizer(tokenize_function)


@pytest.mark.parametrize(
    "dicdir",
    dicdirs,
)
def test_can_generate_tokenizer(dicdir):
    generate_tokenizer(dicdir=dicdir)


@pytest.mark.parametrize(
    "dicdir",
    dicdirs,
)
def test_generate_tokenizer_raises_error_if_node_format_is_invalid(dicdir):
    with pytest.raises(InvalidTokenizerError):
        generate_tokenizer(dicdir=dicdir, node_format=r"%m%H\\n")


def test_generated_tokenizer_returns_unknown_token_as_noun(monkeypatch):
    def find_node_format(dicdir: Optional[str] = None):
        return ""

    def mecab_tagger(
        dicdir: Optional[str] = None,
        node_format: Optional[str] = None,
        unk_format: Optional[str] = None,
    ):
        class MecabTagger:
            def parse(self, text):
                return None

        tagger = MecabTagger()
        return tagger

    def check_tokenizer(tokenize: Callable[[str], List[Word]]) -> None:
        return None

    monkeypatch.setattr(MODULE_TO_BE_TESTED, "_find_node_format", find_node_format)
    monkeypatch.setattr(MODULE_TO_BE_TESTED, "_mecab_tagger", mecab_tagger)
    monkeypatch.setattr(MODULE_TO_BE_TESTED, "check_tokenizer", check_tokenizer)

    tokenize = generate_tokenizer()
    text = "これは未知語です！"
    words = tokenize(text)
    assert len(words) == 1
    assert words[0].surface == text
    assert type(words[0].pos) == Noun
