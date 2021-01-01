from pprint import pprint
from typing import Callable, List, Type

from visedit import StringEdit
from youcab.word import Word
from youcab.youcab import check_tokenizer

from .cform import CForm, Renyo, RenyoOnbin
from .ctype import ALL_CTYPE, get_normalized_ctype
from .errors import UnknownCTypeError
from .utils import debug_on


def show_details(func):
    def _show_details(self, word: Word, cform: Type[CForm]) -> Word:
        before = str(word)
        new_word = func(self, word, cform)
        after = str(new_word)
        if debug_on():
            all_args = str(word) + ", " + str(cform.name)
            print(f"{self.__class__.__name__}.{func.__name__}({all_args}): ")
            if before != after:
                diff = StringEdit(before, after).generate_text(truncate=True)
                diff = "  " + diff.replace("\n", "\n  ")
                print(diff)
        return new_word

    return _show_details


class Conjugation:
    def __init__(self, tokenize: Callable[[str], List[Word]]):
        check_tokenizer(tokenize)
        self.tokenize = tokenize
        self._ending_dic = {
            ctype: ctype.generate_ending_dic(tokenize) for ctype in ALL_CTYPE
        }
        if debug_on():
            pprint(self._ending_dic)

    @show_details
    def conjugate(self, word: Word, cform: Type[CForm]) -> Word:
        try:
            ctype = get_normalized_ctype(word)
            if cform == RenyoOnbin and RenyoOnbin not in self._ending_dic[ctype]:
                cform = Renyo
            ending = self._ending_dic[ctype][cform]
        except (UnknownCTypeError, KeyError):
            return word
        surface = ctype.conjugate(word.base, ending)
        conjugated_word = Word(
            surface=surface,
            pos=word.pos,
            base=word.base,
            c_type=word.c_type,
            c_form=str(cform.name),
        )
        return conjugated_word
