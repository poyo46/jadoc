from abc import ABCMeta, abstractmethod
from typing import List, Type


class PartOfSpeech(metaclass=ABCMeta):
    """
    See Also
    --------
    ``https://www.sketchengine.eu/tagset-jp-mecab/``
    """

    def __init__(self, value: List[str]) -> None:
        self.value = value

    @staticmethod
    @abstractmethod
    def conforms_to(pos_info: List[str]) -> bool:
        pass

    def __str__(self) -> str:
        return self.__class__.__name__ + "(" + str(self.value) + ")"


class AdjectivalNoun(PartOfSpeech):
    """
    形状詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] == "形状詞"


class Adjective(PartOfSpeech):
    """
    形容詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        is_suffix_type = (
            len(pos_info) > 1 and pos_info[0] == "接尾辞" and "形容詞" in pos_info[1]
        )
        return is_suffix_type or pos_info[0] == "形容詞"


class Adnominal(PartOfSpeech):
    """
    連体詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return any(pos.startswith("連体詞") for pos in pos_info)


class Adverb(PartOfSpeech):
    """
    副詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] == "副詞"


class Auxiliary(PartOfSpeech):
    """
    助動詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] in ("助動詞", "判定詞")


class Conjunction(PartOfSpeech):
    """
    接続詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] == "接続詞"


class Interjection(PartOfSpeech):
    """
    感動詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] in ("感動詞", "フィラー")


class Noun(PartOfSpeech):
    """
    名詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0].endswith("名詞")


class Particle(PartOfSpeech):
    """
    助詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] == "助詞"


class EndingParticle(Particle):
    """
    終助詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        is_particle = Particle.conforms_to(pos_info)
        is_ending = len(pos_info) > 1 and "終助詞" in pos_info[1]
        return is_particle and is_ending


class Prefix(PartOfSpeech):
    """
    接頭辞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0].startswith("接頭")


class Suffix(PartOfSpeech):
    """
    接尾辞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return not Adjective.conforms_to(pos_info) and pos_info[0] == "接尾辞"


class Symbol(PartOfSpeech):
    """
    記号
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] in ("記号", "補助記号", "空白", "特殊")


class Verb(PartOfSpeech):
    """
    動詞
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] == "動詞"


class Other(PartOfSpeech):
    """
    その他
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return pos_info[0] in ("その他", "未定義語", "未知語")


class Unknown(PartOfSpeech):
    """
    Unknown part-of-speech
    """

    @staticmethod
    def conforms_to(pos_info: List[str]) -> bool:
        return False


ALL_POS: List[Type[PartOfSpeech]] = [
    AdjectivalNoun,
    Adjective,
    Adnominal,
    Adverb,
    Auxiliary,
    Conjunction,
    Interjection,
    Noun,
    EndingParticle,
    Particle,
    Prefix,
    Suffix,
    Symbol,
    Verb,
    Other,
]


def get_normalized_pos(pos_info: List[str]) -> PartOfSpeech:
    for pos in ALL_POS:
        if pos.conforms_to(pos_info):
            return pos(value=pos_info)
    return Unknown(value=pos_info)
