from typing import Dict, List, Type

import pytest
from youcab.word import Word

from jadoc.cform import CForm
from jadoc.ctype import (
    ALL_CTYPE,
    Adjective,
    AuxiliaryDa,
    AuxiliaryNai,
    CType,
    Godan,
    GodanI,
    GodanN,
    GodanU,
    GodanZ,
    Ichidan,
    Kahen,
    Sahen,
    get_normalized_ctype,
)
from jadoc.errors import UnknownCTypeError

ctype_words: Dict[Type[CType], List[Word]] = {
    Godan: [Word("x", ["x"], c_type="x五段x", c_form="x")],
    GodanI: [
        Word("x", ["x"], base="書く", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="泳ぐ", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="ござる", c_type="x五段x", c_form="x"),
    ],
    GodanZ: [
        Word("x", ["x"], base="立つ", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="売る", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="歌う", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="行く", c_type="x五段x", c_form="x"),
    ],
    GodanN: [
        Word("x", ["x"], base="死ぬ", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="遊ぶ", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="読む", c_type="x五段x", c_form="x"),
    ],
    GodanU: [
        Word("x", ["x"], base="問う", c_type="x五段x", c_form="x"),
        Word("x", ["x"], base="請う", c_type="x五段x", c_form="x"),
    ],
    Ichidan: [
        Word("x", ["x"], base="x", c_type="x一段x", c_form="x"),
    ],
    Kahen: [
        Word("x", ["x"], base="x", c_type="xカx変x", c_form="x"),
    ],
    Sahen: [
        Word("x", ["x"], base="x", c_type="xサx変x", c_form="x"),
    ],
    Adjective: [
        Word("x", pos=["形容詞"], base="x", c_type="x", c_form="x"),
        Word("x", pos=["x"], base="x", c_type="x形容詞活用x", c_form="x"),
    ],
    AuxiliaryDa: [Word("x", pos=["助動詞"], base="だ", c_type="x", c_form="x")],
    AuxiliaryNai: [
        Word("x", pos=["助動詞"], base="ない", c_type="x", c_form="x"),
    ],
}

unknown_word = Word("x", ["x"], c_type="x", c_form="x")


class TestCType:
    @pytest.mark.parametrize(
        "ctype",
        ALL_CTYPE,
    )
    def test_name_should_be_set(self, ctype: Type[CType]):
        assert ctype.name != ""

    @pytest.mark.parametrize("ctype", ALL_CTYPE)
    @pytest.mark.parametrize("ctype_, words", ctype_words.items())
    def test_is_ctype_of(
        self, ctype: Type[CType], ctype_: Type[CType], words: List[Word]
    ):
        if ctype_ == ctype:
            expect = True
        elif ctype == Godan and ctype_ in (GodanI, GodanZ, GodanN, GodanU):
            expect = True
        else:
            expect = False
        for word in words:
            info = (ctype.name, ctype_.name, str(word))
            assert ctype.is_ctype_of(word) == expect, info

    @pytest.mark.parametrize("ctype", ALL_CTYPE)
    def test_unknown(self, ctype: Type[CType]):
        assert not ctype.is_ctype_of(unknown_word)

    @pytest.mark.parametrize(
        "ctype",
        ALL_CTYPE,
    )
    def test_generate_ending_dic(self, ctype: Type[CType], tokenizers):
        for tokenize in tokenizers:
            ending_dic = ctype.generate_ending_dic(tokenize)
            for cform, surface in ending_dic.items():
                assert issubclass(cform, CForm)

    @pytest.mark.parametrize(
        "ctype, base, ending, expect",
        [
            (Godan, "晒す", "a", "晒さ"),
            (Godan, "書く", "い", "書い"),
            (GodanI, "書く", "oう", "書こう"),
            (GodanZ, "立つ", "i", "立ち"),
            (GodanN, "読む", "u", "読む"),
            (GodanU, "問う", "e", "問え"),
            (Ichidan, "食べる", "よう", "食べよう"),
            (Kahen, "くる", "こ", "こ"),
            (Kahen, "やってくる", "き", "やってき"),
            (Kahen, "来る", "こ", "来"),
            (Kahen, "やって来る", "こ", "やって来"),
            (Sahen, "する", "しよう", "しよう"),
            (Sahen, "読書する", "しよう", "読書しよう"),
            (Sahen, "論ずる", "すれ", "論ずれ"),
            (Adjective, "楽しい", "かろう", "楽しかろう"),
            (AuxiliaryDa, "だ", "だっ", "だっ"),
            (AuxiliaryNai, "ない", "かっ", "なかっ"),
        ],
    )
    def test_conjugate(self, ctype: Type[CType], base: str, ending: str, expect: str):
        assert ctype.conjugate(base, ending) == expect


class TestGodan:
    """
    Godan 活用に特有のテスト
    """

    @pytest.mark.parametrize(
        "text, expect",
        [
            ("かみなり", "aみなり"),
            ("ばびろん", "aびろん"),
            ("こぺるにくす", "oぺるにくす"),
            ("ぼうけん", "oうけん"),
        ],
    )
    def test_replace_with_vowel(self, text: str, expect: str):
        assert Godan.replace_with_vowel(text) == expect

    @pytest.mark.parametrize(
        "text",
        [
            "あ行の言葉",
            "ぱ行の言葉",
            "カタカナ",
            "alphabet",
        ],
    )
    def test_replace_with_vowel_should_raise_error(self, text: str):
        with pytest.raises(ValueError):
            Godan.replace_with_vowel(text)


class TestGetNormalizedCType:
    @pytest.mark.parametrize("ctype, words", ctype_words.items())
    def test_should_get_ctype(self, ctype: Type[CType], words: List[Word]):
        for word in words:
            info = (ctype.name, str(word))
            assert get_normalized_ctype(word) == ctype, info

    @pytest.mark.parametrize("ctype", ALL_CTYPE)
    def test_should_be_self_consistent(self, ctype: Type[CType]):
        word = Word("x", ["x"], c_type=str(ctype.name), c_form="x")
        assert get_normalized_ctype(word) == ctype

    def test_unknown_ctype(self):
        with pytest.raises(UnknownCTypeError):
            get_normalized_ctype(unknown_word)
