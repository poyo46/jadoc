from typing import List

import pytest
from youcab.word import Word

from jadoc.cform import Meirei, RenyoOnbin, get_normalized_cform
from jadoc.conj import Conjugation


def are_same_word(words: List[Word]) -> bool:
    assert len(words) >= 2
    surface = words[0].surface
    cform = get_normalized_cform(words[0])
    for word in words:
        if word.surface != surface:
            return False
        if get_normalized_cform(word) != cform:
            return False
    return True


class TestConjugation:
    @pytest.mark.parametrize(
        "word, cform, expect",
        [
            (
                Word("書か", ["動詞", "自立"], "書く", "五段・カ行イ音便", "未然形"),
                Meirei,
                Word("書け", ["動詞", "自立"], "書く", "五段・カ行イ音便", "命令ｅ"),
            ),
            (
                Word("書か", ["動詞", "自立"], "書く", "五段・カ行イ音便", "未然形"),
                RenyoOnbin,
                Word("書い", ["動詞", "自立"], "書く", "五段・カ行イ音便", "連用タ接続"),
            ),
            (
                Word("食べる", ["動詞", "自立"], "食べる", "一段", "基本形"),
                RenyoOnbin,
                Word("食べ", ["動詞", "自立"], "食べる", "一段", "連用形"),
            ),
            (
                Word("x", ["x"], c_type="x", c_form="終止形"),
                Meirei,
                Word("x", ["x"], c_type="x", c_form="終止形"),
            ),
        ],
    )
    def test_conjugate(self, tokenizers, word, cform, expect):
        for tokenize in tokenizers:
            conjugation = Conjugation(tokenize)
            conjugated_word = conjugation.conjugate(word, cform)
            assert are_same_word([conjugated_word, expect])
