from abc import ABCMeta, abstractmethod
from typing import List, Type

from .pos import Adjective, Auxiliary


class ConjugationForm(metaclass=ABCMeta):
    """
    See Also
    --------
    ``https://www.sketchengine.eu/tagset-jp-mecab/``
    """

    def __init__(self, value: str) -> None:
        self.value = value

    @staticmethod
    @abstractmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__ + "(" + self.value + ")"


class Mizen(ConjugationForm):
    """
    未然形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return (
            not IshiSuiryo.conforms_to(surface, pos_info, c_form_info)
            and "未然" in c_form_info
        )


class IshiSuiryo(ConjugationForm):
    """
    意志推量形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        is_daro = surface == "だろ" and c_form_info == "未然形"
        is_desyo = surface == "でしょ" and c_form_info == "未然形"
        is_irregular = is_daro or is_desyo
        return "意志推量" in c_form_info or "未然ウ接続" in c_form_info or is_irregular


class Renyo(ConjugationForm):
    """
    連用形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return "連用" in c_form_info


class RenyoOnbin(ConjugationForm):
    """
    連用形-音便
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        is_onbin = "音便" in c_form_info or "連用タ接続" in c_form_info
        return Renyo.conforms_to(surface, pos_info, c_form_info) and is_onbin


class RenyoNi(ConjugationForm):
    """
    連用形-ニ
    only ``ctype.AuxiliaryDa`` has this conjugation form.
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        is_ni = "ニ" in c_form_info
        return Renyo.conforms_to(surface, pos_info, c_form_info) and is_ni


class Shushi(ConjugationForm):
    """
    終止形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return "終止" in c_form_info or "基本" in c_form_info


class Rentai(ConjugationForm):
    """
    連体形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return "連体" in c_form_info or "体言接続" in c_form_info


class Katei(ConjugationForm):
    """
    仮定形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return "仮定" in c_form_info


class Meirei(ConjugationForm):
    """
    命令形
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return "命令" in c_form_info


class Gokan(ConjugationForm):
    """
    語幹
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        pos_condition = Adjective.conforms_to(pos_info) or Auxiliary.conforms_to(
            pos_info
        )
        return pos_condition and c_form_info in ("ガル接続", "語幹-一般")


class Nothing(ConjugationForm):
    """
    No conjugation
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return c_form_info == ""


class Unknown(ConjugationForm):
    """
    Unknown conjugation form
    """

    @staticmethod
    def conforms_to(surface: str, pos_info: List[str], c_form_info: str) -> bool:
        return False


ALL_CFORM: List[Type[ConjugationForm]] = [
    IshiSuiryo,
    Mizen,
    RenyoNi,
    RenyoOnbin,
    Renyo,
    Shushi,
    Rentai,
    Katei,
    Meirei,
    Gokan,
    Nothing,
]


def get_normalized_cform(
    surface: str, pos_info: List[str], c_form_info: str
) -> ConjugationForm:
    for cform in ALL_CFORM:
        if cform.conforms_to(surface, pos_info, c_form_info):
            return cform(value=c_form_info)
    return Unknown(value=c_form_info)
