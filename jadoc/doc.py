from typing import List, Optional, Union

from .conj import Conjugation
from .mecab.tokenizer import generate_tokenizer
from .utils import debug_on
from .word.cform import ConjugationForm, Mizen, Renyo, RenyoOnbin
from .word.ctype import Sahen
from .word.word import Word


def show_details(func):
    def _show_details(self, *args, **kwargs) -> None:
        before = self.simple_view()
        result = func(self, *args, **kwargs)
        after = self.simple_view()
        if debug_on():
            all_args = ", ".join(
                [str(a) for a in args] + [f"{k}={str(v)}" for k, v in kwargs.items()]
            )
            print(f"{self.__class__.__name__}.{func.__name__}({all_args}): ")
            if before != after:
                print(before)
                print(after)
        return result

    return _show_details


class Doc:
    def __init__(self, text: str, conjugation: Conjugation = None) -> None:
        if conjugation is None:
            conjugation = Conjugation(tokenize=generate_tokenizer())
        self.conjugation = conjugation
        self.words: List[Word] = self.conjugation.tokenize(text)
        if debug_on():
            print("Doc.__init__(): \n" + self.simple_view())

    def _is_within_range(self, interval: Union[int, range]) -> bool:
        index_max = len(self.words) - 1
        if type(interval) == int:
            return 0 <= interval <= index_max
        else:
            return 0 <= interval.start <= (interval.stop - 1) <= index_max

    def get_text(self, interval: Optional[Union[int, range]] = None) -> str:
        if interval is None:
            interval = range(0, len(self.words))
        if type(interval) == int:
            interval = range(interval, interval + 1)

        surface = ""
        for i in interval:
            surface += self.words[i].surface
        return surface

    @show_details
    def retokenize(self, text: Optional[str] = None) -> None:
        if text is None:
            text = self.get_text()
        self.words = self.conjugation.tokenize(text)

    @show_details
    def _conjugate_irregularly(self, i: int, c_form: ConjugationForm) -> bool:
        """
        Returns
        -------
        True
            If this is an irregular case and conjugation has done.
        False
            Otherwise.
        """
        ctype = type(self.words[i].c_type)
        cform = type(c_form)

        # irregular case of 「ある」
        is_aru_mizen_case = all(
            [
                self.words[i].base == "ある",
                cform == Mizen,
                self._is_within_range(i + 1) and self.words[i + 1].base == "ない",
            ]
        )
        if is_aru_mizen_case:
            del self.words[i]
            return True

        # irregular case of 「する」
        is_suru_mizen_case = (
            ctype == Sahen and cform == Mizen and self._is_within_range(i + 1)
        )
        if is_suru_mizen_case:
            if self.words[i + 1].base in ("せる", "れる"):
                self.words[i].surface = "さ"
                self.words[i].c_form = Mizen(value="未然形")
                return True
            elif self.words[i + 1].base == "ぬ":
                self.words[i].surface = "せ"
                self.words[i].c_form = Mizen(value="未然形")
                return True

        return False

    @show_details
    def _conjugate_renyo_onbin(self, i: int) -> None:
        surface = self.words[i + 1].surface
        s = surface[0]

        renyo_onbin = RenyoOnbin(value="連用形-音便")
        self.conjugation.conjugate(self.words[i], renyo_onbin)

        if self.words[i].base[-1] in "ぬぶむ":
            s = s.replace("た", "だ").replace("て", "で")
        else:
            s = s.replace("だ", "た").replace("で", "て")
        self.words[i + 1].surface = s + surface[1:]

    @show_details
    def conjugate(self, i: int, c_form: ConjugationForm) -> None:
        if not self._is_within_range(i):
            return

        if self._conjugate_irregularly(i, c_form):
            return

        # normal case
        self.conjugation.conjugate(self.words[i], c_form)

        cform = type(c_form)
        # post-processing in the case of renyo-onbin
        is_renyo_onbin_case = all(
            [
                cform == Renyo or cform == RenyoOnbin,
                self._is_within_range(i + 1) and self.words[i + 1].surface[0] in "ただてで",
            ]
        )
        if is_renyo_onbin_case:
            self._conjugate_renyo_onbin(i)

    @show_details
    def insert(self, i: int, words: Union[Word, List[Word]]) -> None:
        if type(words) == Word:
            words = [words]
        self.words[i:i] = words

        c_form = self.words[i - 1].c_form
        self.conjugate(i - 1, c_form)
        self.conjugate(i - 1 + len(words), c_form)

    @show_details
    def delete(self, interval: Union[int, range]) -> None:
        if type(interval) == int:
            interval = range(interval, interval + 1)

        if not self._is_within_range(interval):
            return

        c_form = self.words[interval.stop - 1].c_form
        del self.words[interval.start : interval.stop]
        self.conjugate(interval.start - 1, c_form)

    @show_details
    def update(
        self, interval: Union[int, range], words: Union[Word, List[Word]]
    ) -> None:
        if type(interval) == int:
            interval = range(interval, interval + 1)
        if not self._is_within_range(interval):
            return
        if type(words) == Word:
            words = [words]

        n = len(words)
        self.insert(interval.start, words)
        self.delete(range(interval.start + n, interval.stop + n))

    @show_details
    def update_surfaces(
        self, interval: Union[int, range], surfaces: Union[str, List[str]]
    ) -> None:
        if type(interval) == int:
            interval = range(interval, interval + 1)
        if not self._is_within_range(interval):
            return
        if type(surfaces) == str:
            surfaces = [surfaces]

        pre = self.get_text(range(0, interval.start))
        surface = "".join(surfaces)
        post = self.get_text(range(interval.stop, len(self.words)))
        text = pre + surface + post
        self.retokenize(text)

    def simple_view(self, sep: str = "/") -> str:
        tokens = []
        for word in self.words:
            token = word.surface + "[" + str(word.pos)[:3] + "]"
            if word.has_conjugation:
                token += "(" + str(word.c_type)[:3] + ";" + str(word.c_form)[:3] + ")"
            tokens.append(token)

        return sep.join(tokens)

    def copy(self) -> "Doc":
        return Doc(self.get_text(), self.conjugation)
