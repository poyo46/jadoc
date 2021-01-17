from pprint import pprint
from typing import Callable, Dict, List, Optional, Type

from .utils import debug_on
from .word.cform import (
    ConjugationForm,
    Gokan,
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
from .word.ctype import (
    ALL_CTYPE,
    Adjective,
    AuxiliaryDa,
    AuxiliaryNai,
    Godan,
    GodanI,
    GodanN,
    GodanU,
    GodanZ,
    Ichidan,
    Kahen,
    Sahen,
)
from .word.word import Word


def _replace_with_vowel(hiragana_text: str) -> str:
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
    >>> assert _replace_with_vowel("こんにちは") == "oんにちは"
    >>> assert _replace_with_vowel("たのしい") == "aのしい"
    """
    for vowel, chars in Godan.JA_CHARS.items():
        if hiragana_text[0] in chars:
            return vowel + hiragana_text[1:]
    raise ValueError("Could not find the vowel of " + hiragana_text[0])


def show_details(func):
    def _show_details(self, word: Word, c_form: ConjugationForm) -> Word:
        before = str(word)
        new_word = func(self, word, c_form)
        after = str(new_word)
        if debug_on():
            all_args = str(word) + ", " + str(c_form)
            print(f"{self.__class__.__name__}.{func.__name__}({all_args}): ")
            if before != after:
                print(before)
                print(after)
        return new_word

    return _show_details


class Conjugation:
    def __init__(self, tokenize: Callable[[str], List[Word]]):
        self.tokenize = tokenize
        self._ending_dic = {ctype: {} for ctype in ALL_CTYPE}
        self._ending_dic[Godan] = self._generate_godan_ending_dic()
        self._ending_dic[GodanI] = self._generate_godan_ending_dic(renyo_onbin="い")
        self._ending_dic[GodanZ] = self._generate_godan_ending_dic(renyo_onbin="っ")
        self._ending_dic[GodanN] = self._generate_godan_ending_dic(renyo_onbin="ん")
        self._ending_dic[GodanU] = self._generate_godan_ending_dic(renyo_onbin="う")
        self._ending_dic[Ichidan] = self._generate_ichidan_ending_dic()
        self._ending_dic[Kahen] = self._generate_kahen_ending_dic()
        self._ending_dic[Sahen] = self._generate_sahen_ending_dic()
        self._ending_dic[Adjective] = self._generate_adjective_ending_dic()
        self._ending_dic[AuxiliaryDa] = self._generate_auxiliary_da_ending_dic()
        self._ending_dic[AuxiliaryNai] = self._generate_adjective_ending_dic()
        if debug_on():
            pprint(self._ending_dic)

    def _generate_godan_ending_dic(
        self, renyo_onbin: Optional[str] = None
    ) -> Dict[Type[ConjugationForm], str]:
        words = self.tokenize("書かない。書こう。書きます。書く。書くとき。書けば。書け！")
        cforms = [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei]
        endings = [
            _replace_with_vowel(word.surface[1:])
            for word in words
            if isinstance(word.c_type, Godan)
        ]
        assert len(cforms) == len(endings)
        ending_dic = {c: e for c, e in zip(cforms, endings)}
        if renyo_onbin is not None:
            ending_dic[RenyoOnbin] = renyo_onbin
        return ending_dic

    def _generate_ichidan_ending_dic(self) -> Dict[Type[ConjugationForm], str]:
        words = self.tokenize("起きない。起きよう。起きます。起きる。起きるとき。起きれば。起きろ！")
        cforms = [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei]
        endings = [word.surface[2:] for word in words if type(word.c_type) == Ichidan]
        assert len(cforms) == len(endings)
        return {c: e for c, e in zip(cforms, endings)}

    def _generate_kahen_ending_dic(self) -> Dict[Type[ConjugationForm], str]:
        words = self.tokenize("持ってこない。持ってこよう。持ってきます。持ってくる。持ってくるとき。持ってくれば。持ってこい。")
        cforms = [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei]
        endings = [word.surface for word in words if type(word.c_type) == Kahen]
        assert len(cforms) == len(endings)
        return {c: e for c, e in zip(cforms, endings)}

    def _generate_sahen_ending_dic(self) -> Dict[Type[ConjugationForm], str]:
        words = self.tokenize("すぐしない。読書しよう。します。する。するとき。すれば。読書せよ！")
        cforms = [Mizen, IshiSuiryo, Renyo, Shushi, Rentai, Katei, Meirei]
        endings = [word.surface for word in words if type(word.c_type) == Sahen]
        assert len(cforms) == len(endings)
        return {c: e for c, e in zip(cforms, endings)}

    def _generate_adjective_ending_dic(self) -> Dict[Type[ConjugationForm], str]:
        words = self.tokenize("美しかろう。美しく咲く。美しかった。美しい。美しいとき。美しければ。美しそう。")
        cforms = [IshiSuiryo, Renyo, RenyoOnbin, Shushi, Rentai, Katei, Gokan]
        endings = [word.surface[2:] for word in words if type(word.c_type) == Adjective]
        assert len(cforms) == len(endings)
        return {c: e for c, e in zip(cforms, endings)}

    def _generate_auxiliary_da_ending_dic(self) -> Dict[Type[ConjugationForm], str]:
        words = self.tokenize("鯖だろう。鯖である。鯖だった。鯖だ。鯖なの。鯖ならば。")
        cforms = [IshiSuiryo, Renyo, RenyoOnbin, Shushi, Rentai, Katei]
        endings = [word.surface for word in words if type(word.c_type) == AuxiliaryDa]
        assert len(cforms) == len(endings)
        ending_dic = {c: e for c, e in zip(cforms, endings)}
        ending_dic[RenyoNi] = "に"
        return ending_dic

    @show_details
    def conjugate(self, word: Word, c_form: ConjugationForm) -> Word:
        if not word.has_conjugation:
            return word

        ctype = type(word.c_type)
        cform = type(c_form)

        try:
            if cform == RenyoOnbin and RenyoOnbin not in self._ending_dic[ctype]:
                c_form = Renyo(value="連用形")
                cform = type(c_form)
            ending = self._ending_dic[ctype][cform]
            if not word.base.endswith("しい") and cform == Gokan:
                ending = "さ"  # 語幹-サ
        except KeyError:
            return word

        word.surface = ctype.conjugate(word.base, ending)
        word.c_form = c_form

        return word
