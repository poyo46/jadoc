from typing import Dict, List, Type

import pytest

from jadoc.word.pos import (
    ALL_POS,
    AdjectivalNoun,
    Adjective,
    Adnominal,
    Adverb,
    Auxiliary,
    Conjunction,
    Interjection,
    Noun,
    Other,
    Particle,
    PartOfSpeech,
    Prefix,
    Suffix,
    Symbol,
    Unknown,
    Verb,
    get_normalized_pos,
)

examples: Dict[Type[PartOfSpeech], List[List[str]]] = {
    Adjective: [["形容詞", "x"]],
    Adnominal: [["連体詞", "x"], ["x", "連体詞"]],
    Adverb: [["副詞", "x"]],
    AdjectivalNoun: [["形状詞", "x"]],
    Auxiliary: [["助動詞", "x"], ["判定詞", "x"]],
    Conjunction: [["接続詞", "x"]],
    Interjection: [["感動詞", "x"], ["フィラー", "x"]],
    Noun: [["x名詞", "x"]],
    Particle: [["助詞", "x"]],
    Prefix: [["接頭x", "x"]],
    Suffix: [["接尾辞", "x"]],
    Symbol: [["記号", "x"], ["補助記号", "x"], ["空白", "x"], ["特殊", "x"]],
    Verb: [["動詞", "x"]],
    Other: [["その他", "x"], ["未定義語", "x"], ["未知語", "x"]],
    Unknown: [["x"]],
}


@pytest.mark.parametrize("pos", ALL_POS)
@pytest.mark.parametrize("pos_, info_list", examples.items())
def test_conforms_to(
    pos: Type[PartOfSpeech], pos_: Type[PartOfSpeech], info_list: List[str]
):
    if pos == pos_:
        expect = True
    else:
        expect = False
    for pos_info in info_list:
        err_msg = (pos.__name__, pos_.__name__, str(pos_info))
        assert pos.conforms_to(pos_info) == expect, err_msg


@pytest.mark.parametrize("pos, info_list", examples.items())
def test_get_normalized_pos(pos: Type[PartOfSpeech], info_list: List[str]):
    for pos_info in info_list:
        pos_ = get_normalized_pos(pos_info)
        assert type(pos_) == pos
        assert pos_.value == pos_info
