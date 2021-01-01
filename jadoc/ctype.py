from abc import ABCMeta, abstractmethod
from typing import Callable, Dict, List, Type

from youcab.word import Word

from . import pos
from .cform import (
    CForm,
    IshiSuiryo,
    Katei,
    Meirei,
    Mizen,
    Rentai,
    Renyo,
    RenyoNi,
    RenyoOnbin,
    Shushi,
)
from .errors import UnknownCTypeError


class CType(metaclass=ABCMeta):
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
    def is_ctype_of(word: Word) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        """
        活用辞書を生成する。
        """
        pass

    @staticmethod
    @abstractmethod
    def conjugate(base: str, ending: str) -> str:
        """
        活用した結果の表層形を得る。
        """
        pass


def _ending_dic_generator(
    tokenize: Callable[[str], List[Word]],
    text: str,
    ending_getter: Callable[[Word], str],
    cforms: List[Type[CForm]],
    ctype: Type[CType],
) -> Dict[Type[CForm], str]:
    words = tokenize(text)
    endings = [ending_getter(word) for word in words if ctype.is_ctype_of(word)]
    assert len(cforms) == len(endings)
    return {c: e for c, e in zip(cforms, endings)}


class Godan(CType):
    """
    五段活用
    """

    name = "五段活用"

    POLITE = ("ござる", "御座る", "なさる", "為さる", "くださる", "下さる", "おっしゃる", "仰る", "いらっしゃる")
    JA_CHARS = {
        "a": ("か", "さ", "た", "な", "は", "ま", "ら", "わ", "が", "ざ", "だ", "ば"),
        "i": ("き", "し", "ち", "に", "ひ", "み", "り", "い", "ぎ", "じ", "ぢ", "び"),
        "u": ("く", "す", "つ", "ぬ", "ふ", "む", "る", "う", "ぐ", "ず", "づ", "ぶ"),
        "e": ("け", "せ", "て", "ね", "へ", "め", "れ", "え", "げ", "ぜ", "で", "べ"),
        "o": ("こ", "そ", "と", "の", "ほ", "も", "ろ", "お", "ご", "ぞ", "ど", "ぼ"),
    }

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return "五段" in word.c_type

    @staticmethod
    def replace_with_vowel(hiragana_text: str) -> str:
        """
        Replace the first letter of ``hiragana_text`` with its vowel.

        Parameters
        ----------
        hiragana_text : str
            A string of Japanese hiragana characters.

        Returns
        -------
        str
            ``hiragana_text`` after replacement.

        Raises
        ------
        ValueError
            If the vowel of ``hiragana_text[0]`` is not found.

        Examples
        --------
        >>> assert Godan.replace_with_vowel("こんにちは") == "oんにちは"
        >>> assert Godan.replace_with_vowel("たのしい") == "aのしい"
        """
        for vowel, chars in Godan.JA_CHARS.items():
            if hiragana_text[0] in chars:
                return vowel + hiragana_text[1:]
        raise ValueError("Could not find the vowel of " + hiragana_text[0])

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        return _ending_dic_generator(
            tokenize,
            "書かない。書こう。書きます。書く。書くとき。書けば。書け！",
            lambda word: Godan.replace_with_vowel(word.surface[1:]),
            [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei],
            Godan,
        )

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        e = ending[0]
        if e not in Godan.JA_CHARS.keys():
            return base[:-1] + e
        u = base[-1]
        idx = Godan.JA_CHARS["u"].index(u)
        ending = Godan.JA_CHARS[e][idx] + ending[1:]
        return base[:-1] + ending


class GodanI(CType):
    """
    五段活用（イ音便）
    """

    name = "五段活用（イ音便）"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        s = word.base
        is_i_onbin = any(
            [s[-1] in "くぐ" and not s.endswith(("行く", "逝く")), s.endswith(Godan.POLITE)]
        )
        return Godan.is_ctype_of(word) and is_i_onbin or GodanI.name in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        ending_dic = Godan.generate_ending_dic(tokenize)
        ending_dic[RenyoOnbin] = "い"
        return ending_dic

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return Godan.conjugate(base, ending)


class GodanZ(CType):
    """
    五段活用（促音便）
    """

    name = "五段活用（促音便）"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        s = word.base
        is_z_onbin = all(
            [
                s[-1] in "つるう" or s.endswith(("行く", "逝く")),
                not s.endswith(Godan.POLITE),
                not s.endswith(("問う", "請う")),
            ]
        )
        return Godan.is_ctype_of(word) and is_z_onbin or GodanZ.name in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        ending_dic = Godan.generate_ending_dic(tokenize)
        ending_dic[RenyoOnbin] = "っ"
        return ending_dic

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return Godan.conjugate(base, ending)


class GodanN(CType):
    """
    五段活用（撥音便）
    """

    name = "五段活用（撥音便）"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        is_n_onbin = word.base[-1] in "ぬぶむ"
        return Godan.is_ctype_of(word) and is_n_onbin or GodanN.name in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        ending_dic = Godan.generate_ending_dic(tokenize)
        ending_dic[RenyoOnbin] = "ん"
        return ending_dic

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return Godan.conjugate(base, ending)


class GodanU(CType):
    """
    五段活用（ウ音便）

    Notes
    -----
    There are only a few, such as 問う and 請う.
    """

    name = "五段活用（ウ音便）"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        is_u_onbin = word.base.endswith(("問う", "請う"))
        return Godan.is_ctype_of(word) and is_u_onbin or GodanU.name in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        ending_dic = Godan.generate_ending_dic(tokenize)
        ending_dic[RenyoOnbin] = "う"
        return ending_dic

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return Godan.conjugate(base, ending)


class Ichidan(CType):
    """
    一段活用
    """

    name = "一段活用"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return "一段" in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        return _ending_dic_generator(
            tokenize,
            "起きない。起きよう。起きます。起きる。起きるとき。起きれば。起きろ！",
            lambda word: word.surface[2:],
            [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei],
            Ichidan,
        )

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return base[:-1] + ending


class Kahen(CType):
    """
    カ行変格活用
    """

    name = "カ行変格活用"

    TRANS = str.maketrans({"き": "来", "く": "来", "こ": "来"})

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return "カ" in word.c_type and "変" in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        return _ending_dic_generator(
            tokenize,
            "持ってこない。持ってこよう。持ってきます。持ってくる。持ってくるとき。持ってくれば。持ってこい。",
            lambda word: word.surface,
            [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei],
            Kahen,
        )

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        if base.endswith("来る"):
            ending = ending.translate(Kahen.TRANS)
        return base[:-2] + ending


class Sahen(CType):
    """
    サ行変格活用
    """

    name = "サ行変格活用"

    TRANS = str.maketrans(
        {
            "さ": "ざ",
            "し": "じ",
            "す": "ず",
            "せ": "ぜ",
        }
    )

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return "サ" in word.c_type and "変" in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        return _ending_dic_generator(
            tokenize,
            "すぐしない。読書しよう。します。する。するとき。すれば。読書せよ！",
            lambda word: word.surface,
            [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei],
            Sahen,
        )

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        if base.endswith("ずる"):
            ending = ending.translate(Sahen.TRANS)
        return base[:-2] + ending


class Adjective(CType):
    """
    形容詞活用
    """

    name = "形容詞活用"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return pos.Adjective.is_pos_of(word) or Adjective.name in word.c_type

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        return _ending_dic_generator(
            tokenize,
            "美しかろう。美しく咲く。美しかった。美しい。美しいとき。美しければ。",
            lambda word: word.surface[2:],
            [IshiSuiryo, Renyo, RenyoOnbin, Shushi, Rentai, Katei],
            Adjective,
        )

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return base[:-1] + ending


class AuxiliaryDa(CType):
    """
    助動詞「だ」
    """

    name = "助動詞「だ」"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return (
            pos.Auxiliary.is_pos_of(word)
            and word.base == "だ"
            or AuxiliaryDa.name in word.c_type
        )

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        ending_dic = _ending_dic_generator(
            tokenize,
            "鯖だろう。鯖である。鯖だった。鯖だ。鯖なの。鯖ならば。",
            lambda word: word.surface,
            [IshiSuiryo, Renyo, RenyoOnbin, Shushi, Rentai, Katei],
            AuxiliaryDa,
        )
        ending_dic[RenyoNi] = "に"
        return ending_dic

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return ending


class AuxiliaryNai(CType):
    """
    助動詞「ない」
    """

    name = "助動詞「ない」"

    @staticmethod
    def is_ctype_of(word: Word) -> bool:
        return (
            pos.Auxiliary.is_pos_of(word)
            and word.base == "ない"
            or AuxiliaryNai.name in word.c_type
        )

    @staticmethod
    def generate_ending_dic(
        tokenize: Callable[[str], List[Word]]
    ) -> Dict[Type[CForm], str]:
        return Adjective.generate_ending_dic(tokenize)

    @staticmethod
    def conjugate(base: str, ending: str) -> str:
        return Adjective.conjugate(base, ending)


ALL_CTYPE: List[Type[CType]] = [
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
]


def get_normalized_ctype(word: Word) -> Type[CType]:
    """
    Examples
    --------
    >>> word_write = Word("書い", ["動詞", "一般"], "書く", "五段-カ行", "連用形-イ音便")
    >>> assert get_normalized_ctype(word_write) == GodanI
    """
    for ctype in ALL_CTYPE:
        if ctype.is_ctype_of(word):
            return ctype
    raise UnknownCTypeError(str(word))
