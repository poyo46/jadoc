from typing import Dict, List, Type

import pytest
from youcab.word import Word

from jadoc.cform import (
    ALL_CFORM,
    CForm,
    IshiSuiryo,
    Katei,
    Meirei,
    Mizen,
    Nothing,
    Rentai,
    Renyo,
    RenyoNi,
    RenyoOnbin,
    Shushi,
    get_normalized_cform,
)
from jadoc.errors import UnknownCFormError

cform_words: Dict[Type[CForm], List[Word]] = {
    Mizen: [Word("x", ["x"], c_type="x", c_form="x未然x")],
    IshiSuiryo: [
        Word("x", ["x"], c_type="x", c_form="x意志推量x"),
        Word("x", ["x"], c_type="x", c_form="x未然ウ接続x"),
        Word("だろ", ["x"], c_type="x", c_form="未然形"),
    ],
    Renyo: [
        Word("x", ["x"], c_type="x", c_form="x連用x"),
    ],
    RenyoOnbin: [
        Word("x", ["x"], c_type="x", c_form="x連用x音便x"),
        Word("x", ["x"], c_type="x", c_form="x連用タ接続x"),
    ],
    RenyoNi: [
        Word("x", ["x"], c_type="x", c_form="x連用xニx"),
    ],
    Shushi: [
        Word("x", ["x"], c_type="x", c_form="x終止x"),
        Word("x", ["x"], c_type="x", c_form="x基本x"),
    ],
    Rentai: [
        Word("x", ["x"], c_type="x", c_form="x連体x"),
        Word("x", ["x"], c_type="x", c_form="x体言接続x"),
    ],
    Katei: [
        Word("x", ["x"], c_type="x", c_form="x仮定x"),
    ],
    Meirei: [
        Word("x", ["x"], c_type="x", c_form="x命令x"),
    ],
    Nothing: [Word("x", ["x"])],
}

unknown_word = Word("x", ["x"], c_type="x", c_form="x")


class TestCForm:
    @pytest.mark.parametrize(
        "cform",
        ALL_CFORM,
    )
    def test_name_should_be_set(self, cform: Type[CForm]):
        if cform == Nothing:
            return
        assert cform.name != ""

    @pytest.mark.parametrize("cform", ALL_CFORM)
    @pytest.mark.parametrize("cform_, words", cform_words.items())
    def test_is_cform_of(
        self, cform: Type[CForm], cform_: Type[CForm], words: List[Word]
    ):
        if cform_ == cform:
            expect = True
        elif cform == Renyo and cform_ in (RenyoOnbin, RenyoNi):
            expect = True
        else:
            expect = False
        for word in words:
            info = (cform.name, cform_.name, str(word))
            assert cform.is_cform_of(word) == expect, info

    @pytest.mark.parametrize("cform", ALL_CFORM)
    def test_unknown(self, cform: Type[CForm]):
        assert not cform.is_cform_of(unknown_word)


class TestGetNormalizedCForm:
    @pytest.mark.parametrize("cform, words", cform_words.items())
    def test_should_get_cform(self, cform: Type[CForm], words: List[Word]):
        for word in words:
            info = (cform.name, str(word))
            assert get_normalized_cform(word) == cform, info

    @pytest.mark.parametrize("cform", ALL_CFORM)
    def test_should_be_self_consistent(self, cform: Type[CForm]):
        word = Word("x", ["x"], c_type="x", c_form=str(cform.name))
        assert get_normalized_cform(word) == cform

    def test_unknown_cform(self):
        with pytest.raises(UnknownCFormError):
            get_normalized_cform(unknown_word)
