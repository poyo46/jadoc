from abc import ABCMeta, abstractmethod
from typing import List, Type

from youcab.word import Word

from .errors import UnknownCFormError


class CForm(metaclass=ABCMeta):
    """
    See Also
    --------
    ``https://www.sketchengine.eu/tagset-jp-mecab/``
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def is_cform_of(word: Word) -> bool:
        pass


class Mizen(CForm):
    name = "未然形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return not IshiSuiryo.is_cform_of(word) and "未然" in word.c_form


class IshiSuiryo(CForm):
    name = "意志推量形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        is_irregular = word.surface == "だろ" and word.c_form == "未然形"
        return "意志推量" in word.c_form or "未然ウ接続" in word.c_form or is_irregular


class Renyo(CForm):
    name = "連用形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return "連用" in word.c_form


class RenyoOnbin(CForm):
    name = "連用形-音便"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        is_onbin = "音便" in word.c_form or "連用タ接続" in word.c_form
        return Renyo.is_cform_of(word) and is_onbin


class RenyoNi(CForm):
    """
    only ``ctype.AuxiliaryDa`` has this form.
    """

    name = "連用形-ニ"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        is_ni = "ニ" in word.c_form
        return Renyo.is_cform_of(word) and is_ni


class Shushi(CForm):
    name = "終止形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return "終止" in word.c_form or "基本" in word.c_form


class Rentai(CForm):
    name = "連体形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return "連体" in word.c_form or "体言接続" in word.c_form


class Katei(CForm):
    name = "仮定形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return "仮定" in word.c_form


class Meirei(CForm):
    name = "命令形"

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return "命令" in word.c_form


class Nothing(CForm):
    name = ""

    @staticmethod
    def is_cform_of(word: Word) -> bool:
        return word.c_form == ""


ALL_CFORM: List[Type[CForm]] = [
    IshiSuiryo,
    Mizen,
    RenyoNi,
    RenyoOnbin,
    Renyo,
    Shushi,
    Rentai,
    Katei,
    Meirei,
    Nothing,
]


def get_normalized_cform(word: Word) -> Type[CForm]:
    """
    Examples
    --------
    >>> word = Word("書い", ["動詞", "一般"], "書く", "五段-カ行", "連用形-イ音便")
    >>> assert get_normalized_cform(word) == RenyoOnbin
    """
    for cform in ALL_CFORM:
        if cform.is_cform_of(word):
            return cform
    raise UnknownCFormError(str(word))
