from typing import List

import pytest

from jadoc.conj import Conjugation, _replace_with_vowel
from jadoc.mecab.config import get_dicdirs
from jadoc.mecab.tokenizer import generate_tokenizer
from jadoc.word.cform import Meirei, RenyoOnbin
from jadoc.word.word import Word

tokenizers = [generate_tokenizer(dicdir) for dicdir in get_dicdirs()]


@pytest.mark.parametrize(
    "text, expect",
    [
        ("かみなり", "aみなり"),
        ("ばびろん", "aびろん"),
        ("こぺるにくす", "oぺるにくす"),
        ("ぼうけん", "oうけん"),
    ],
)
def test_replace_with_vowel(text: str, expect: str):
    assert _replace_with_vowel(text) == expect


@pytest.mark.parametrize(
    "text",
    [
        "あ行の言葉",
        "ぱ行の言葉",
        "カタカナ",
        "alphabet",
    ],
)
def test_replace_with_vowel_should_raise_error(text: str):
    with pytest.raises(ValueError):
        _replace_with_vowel(text)


def are_same_word(words: List[Word]) -> bool:
    if len(words) < 2:
        raise ValueError
    surface = words[0].surface
    cform = type(words[0].c_form)
    for word in words:
        if word.surface != surface:
            return False
        if type(word.c_form) != cform:
            return False
    return True


class TestConjugation:
    @pytest.mark.parametrize("tokenize", tokenizers)
    @pytest.mark.parametrize(
        "word, c_form, expect",
        [
            (
                Word("書か", ["動詞", "自立"], "書く", "五段・カ行イ音便", "未然形"),
                Meirei(value="命令形"),
                Word("書け", ["動詞", "自立"], "書く", "五段・カ行イ音便", "命令ｅ"),
            ),
            (
                Word("書か", ["動詞", "自立"], "書く", "五段・カ行イ音便", "未然形"),
                RenyoOnbin(value="連用形-音便"),
                Word("書い", ["動詞", "自立"], "書く", "五段・カ行イ音便", "連用タ接続"),
            ),
            (
                Word("食べる", ["動詞", "自立"], "食べる", "一段", "基本形"),
                RenyoOnbin(value="連用形-音便"),
                Word("食べ", ["動詞", "自立"], "食べる", "一段", "連用形"),
            ),
            (
                Word("x", ["x"], c_type_info="x", c_form_info="終止形"),
                Meirei(value="命令形"),
                Word("x", ["x"], c_type_info="x", c_form_info="終止形"),
            ),
        ],
    )
    def test_conjugate(self, tokenize, word, c_form, expect):
        conjugation = Conjugation(tokenize)
        conjugated_word = conjugation.conjugate(word, c_form)
        assert are_same_word([conjugated_word, expect])
