from abc import ABCMeta, abstractmethod

from youcab.youcab import Word

from .errors import UnknownPosError


class Pos(metaclass=ABCMeta):
    """
    See Also
    --------
    https://www.sketchengine.eu/tagset-jp-mecab/
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @staticmethod
    @abstractmethod
    def is_pos_of(word: Word) -> bool:
        pass


class AdjectivalNoun(Pos):
    """
    形状詞
    """

    name = "形状詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "形状詞"


class Adjective(Pos):
    """
    形容詞
    ``接尾辞-形容詞性述語接尾辞`` をこれに含める？
    """

    name = "形容詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "形容詞"


class Adnominal(Pos):
    """
    連体詞
    """

    name = "連体詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return any(pos.startswith("連体詞") for pos in word.pos)


class Adverb(Pos):
    """
    副詞
    """

    name = "副詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "副詞"


class Auxiliary(Pos):
    """
    助動詞
    """

    name = "助動詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] in ("助動詞", "判定詞")


class Conjunction(Pos):
    """
    接続詞
    """

    name = "接続詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "接続詞"


class Interjection(Pos):
    """
    感動詞
    """

    name = "感動詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] in ("感動詞", "フィラー")


class Noun(Pos):
    """
    名詞
    """

    name = "名詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0].endswith("名詞")


class Particle(Pos):
    """
    助詞
    """

    name = "助詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "助詞"


class Prefix(Pos):
    """
    接頭辞
    """

    name = "接頭辞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0].startswith("接頭")


class Suffix(Pos):
    """
    接尾辞
    """

    name = "接尾辞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "接尾辞"


class Symbol(Pos):
    """
    記号
    """

    name = "記号"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] in ("記号", "補助記号", "空白", "特殊")


class Verb(Pos):
    """
    動詞
    """

    name = "動詞"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] == "動詞"


class Other(Pos):
    """
    その他
    """

    name = "その他"

    @staticmethod
    def is_pos_of(word: Word) -> bool:
        return word.pos[0] in ("その他", "未定義語", "未知語")


ALL_POS = [
    AdjectivalNoun,
    Adjective,
    Adnominal,
    Adverb,
    Auxiliary,
    Conjunction,
    Interjection,
    Noun,
    Particle,
    Prefix,
    Suffix,
    Symbol,
    Verb,
    Other,
]


def get_normalized_pos(word: Word) -> Pos:
    """
    Examples
    --------
    >>> word = Word("楽しい", ["形容詞", "一般"], "楽しい", "形容詞", "連体形")
    >>> assert get_normalized_pos(word) == Adjective
    """
    for pos in ALL_POS:
        if pos.is_pos_of(word):
            return pos
    raise UnknownPosError(str(word))
