from typing import Dict, List, Type

import pytest
from youcab.word import Word

from jadoc.errors import UnknownPosError
from jadoc.pos import (
    ALL_POS,
    AdjectivalNoun,
    Adjective,
    Adnominal,
    Adverb,
    Auxiliary,
    Conjunction,
    Interjection,
    Noun,
    Other,
    Particle,
    Pos,
    Prefix,
    Suffix,
    Symbol,
    Verb,
    get_normalized_pos,
)

pos_words: Dict[Type[Pos], List[Word]] = {
    Adjective: [Word("x", pos=["形容詞", "x"])],
    Adnominal: [
        Word("x", pos=["連体詞", "x"]),
        Word("x", pos=["x", "連体詞"]),
    ],
    Adverb: [Word("x", pos=["副詞", "x"])],
    AdjectivalNoun: [Word("x", pos=["形状詞", "x"])],
    Auxiliary: [Word("x", pos=["助動詞", "x"]), Word("x", pos=["判定詞", "x"])],
    Conjunction: [Word("x", pos=["接続詞", "x"])],
    Interjection: [
        Word("x", pos=["感動詞", "x"]),
        Word("x", pos=["フィラー", "x"]),
    ],
    Noun: [
        Word("x", pos=["x名詞", "x"]),
    ],
    Particle: [
        Word("x", pos=["助詞", "x"]),
    ],
    Prefix: [
        Word("x", pos=["接頭x", "x"]),
    ],
    Suffix: [
        Word("x", pos=["接尾辞", "x"]),
    ],
    Symbol: [
        Word("x", pos=["記号", "x"]),
        Word("x", pos=["補助記号", "x"]),
        Word("x", pos=["空白", "x"]),
        Word("x", pos=["特殊", "x"]),
    ],
    Verb: [
        Word("x", pos=["動詞", "x"]),
    ],
    Other: [
        Word("x", pos=["その他", "x"]),
        Word("x", pos=["未定義語", "x"]),
        Word("x", pos=["未知語", "x"]),
    ],
}

unknown_word = Word("x", pos=["x"])


class TestPos:
    @pytest.mark.parametrize("pos", ALL_POS)
    def test_name_should_be_set(self, pos: Type[Pos]):
        assert pos.name != ""

    @pytest.mark.parametrize("pos", ALL_POS)
    @pytest.mark.parametrize("pos_, words", pos_words.items())
    def test_is_pos_of(self, pos: Type[Pos], pos_: Type[Pos], words: List[Word]):
        if pos_ == pos:
            expect = True
        else:
            expect = False
        for word in words:
            info = (pos.name, pos_.name, str(word))
            assert pos.is_pos_of(word) == expect, info

    @pytest.mark.parametrize("pos", ALL_POS)
    def test_unknown(self, pos):
        assert not pos.is_pos_of(unknown_word)


class TestGetNormalizedPos:
    @pytest.mark.parametrize("pos, words", pos_words.items())
    def test_should_get_pos(self, pos: Type[Pos], words: List[Word]):
        for word in words:
            assert get_normalized_pos(word) == pos, (pos.name, str(word))

    @pytest.mark.parametrize("pos", ALL_POS)
    def test_should_be_self_consistent(self, pos: Type[Pos]):
        word = Word("x", pos=[str(pos.name)])
        assert get_normalized_pos(word) == pos

    def test_unknown_pos(self):
        with pytest.raises(UnknownPosError):
            get_normalized_pos(unknown_word)
