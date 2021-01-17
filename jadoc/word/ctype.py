from abc import ABCMeta, abstractmethod
from typing import List, Type

from jadoc.errors import CannotConjugateError

from . import pos


class ConjugationType(metaclass=ABCMeta):
    """
    See Also
    --------
    ``https://www.sketchengine.eu/tagset-jp-mecab/``
    """

    def __init__(self, value: str) -> None:
        self.value = value

    @staticmethod
    @abstractmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def conjugate(base: str, ending: str) -> str:
        """
        活用した結果の表層形を得る。
        """
        pass

    def __str__(self) -> str:
        return self.__class__.__name__ + "(" + self.value + ")"


class Godan(ConjugationType):
    """
    五段活用
    """

    POLITE = ("ござる", "御座る", "なさる", "為さる", "くださる", "下さる", "おっしゃる", "仰る", "いらっしゃる")
    JA_CHARS = {
        "a": ("か", "さ", "た", "な", "は", "ま", "ら", "わ", "が", "ざ", "だ", "ば"),
        "i": ("き", "し", "ち", "に", "ひ", "み", "り", "い", "ぎ", "じ", "ぢ", "び"),
        "u": ("く", "す", "つ", "ぬ", "ふ", "む", "る", "う", "ぐ", "ず", "づ", "ぶ"),
        "e": ("け", "せ", "て", "ね", "へ", "め", "れ", "え", "げ", "ぜ", "で", "べ"),
        "o": ("こ", "そ", "と", "の", "ほ", "も", "ろ", "お", "ご", "ぞ", "ど", "ぼ"),
    }

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return "五段" in c_type_info

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        e = ending[0]
        if e not in Godan.JA_CHARS.keys():
            return base[:-1] + e
        u = base[-1]
        idx = Godan.JA_CHARS["u"].index(u)
        ending = Godan.JA_CHARS[e][idx] + ending[1:]
        return base[:-1] + ending


class GodanI(Godan):
    """
    五段活用（イ音便）
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        is_i_onbin = (
            base[-1] in "くぐ" and not base.endswith(("行く", "逝く"))
        ) or base.endswith(Godan.POLITE)
        return Godan.conforms_to(pos_info, base, c_type_info) and is_i_onbin


class GodanZ(Godan):
    """
    五段活用（促音便）
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        is_z_onbin = (
            (base[-1] in "つるう" or base.endswith(("行く", "逝く")))
            and (not base.endswith(Godan.POLITE))
            and (not base.endswith(("問う", "請う")))
        )
        return Godan.conforms_to(pos_info, base, c_type_info) and is_z_onbin


class GodanN(Godan):
    """
    五段活用（撥音便）
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        is_n_onbin = base[-1] in "ぬぶむ"
        return Godan.conforms_to(pos_info, base, c_type_info) and is_n_onbin


class GodanU(Godan):
    """
    五段活用（ウ音便）

    Notes
    -----
    There are only a few, such as 問う and 請う.
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        is_u_onbin = base.endswith(("問う", "請う"))
        return Godan.conforms_to(pos_info, base, c_type_info) and is_u_onbin


class Ichidan(ConjugationType):
    """
    一段活用
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return "一段" in c_type_info

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return base[:-1] + ending


class Kahen(ConjugationType):
    """
    カ行変格活用
    """

    TRANS = str.maketrans({"き": "来", "く": "来", "こ": "来"})

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return "カ" in c_type_info and "変" in c_type_info

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        if base.endswith("来る"):
            ending = ending.translate(Kahen.TRANS)
        return base[:-2] + ending


class Sahen(ConjugationType):
    """
    サ行変格活用
    """

    TRANS = str.maketrans(
        {
            "さ": "ざ",
            "し": "じ",
            "す": "ず",
            "せ": "ぜ",
        }
    )

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return "サ" in c_type_info and "変" in c_type_info

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        if base.endswith("ずる"):
            ending = ending.translate(Sahen.TRANS)
        return base[:-2] + ending


class Adjective(ConjugationType):
    """
    形容詞活用
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return pos.Adjective.conforms_to(pos_info)

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return base[:-1] + ending


class AuxiliaryDa(ConjugationType):
    """
    助動詞「だ」
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return pos.Auxiliary.conforms_to(pos_info) and base == "だ"

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return ending


class AuxiliaryNai(ConjugationType):
    """
    助動詞「ない」
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return pos.Auxiliary.conforms_to(pos_info) and base == "ない"

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return Adjective.conjugate(base, ending)


class Nothing(ConjugationType):
    """
    No conjugation
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return c_type_info == ""

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        raise CannotConjugateError


class Unknown(ConjugationType):
    """
    Unknown conjugation form
    """

    @staticmethod
    def conforms_to(pos_info: List[str], base: str, c_type_info: str) -> bool:
        return False

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        raise CannotConjugateError


ALL_CTYPE: List[Type[ConjugationType]] = [
    GodanI,
    GodanZ,
    GodanN,
    GodanU,
    Godan,  # get_normalized_ctype で先頭から順に判定するため五段活用の最後におく
    Ichidan,
    Kahen,
    Sahen,
    Adjective,
    AuxiliaryDa,
    AuxiliaryNai,
    Nothing,
]


def get_normalized_ctype(
    pos_info: List[str], base: str, c_type_info: str
) -> ConjugationType:
    for ctype in ALL_CTYPE:
        if ctype.conforms_to(pos_info, base, c_type_info):
            return ctype(value=c_type_info)
    return Unknown(value=c_type_info)
