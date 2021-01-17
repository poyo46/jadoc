from typing import Dict, List, Type

import pytest

from jadoc.errors import CannotConjugateError
from jadoc.word.ctype import (
    ALL_CTYPE,
    Adjective,
    AuxiliaryDa,
    AuxiliaryNai,
    ConjugationType,
    Godan,
    GodanI,
    GodanN,
    GodanU,
    GodanZ,
    Ichidan,
    Kahen,
    Nothing,
    Sahen,
    Unknown,
    get_normalized_ctype,
)

examples: Dict[Type[ConjugationType], List[Dict[str, str]]] = {
    Godan: [{"pos_info": ["x"], "base": "x", "c_type_info": "x五段x"}],
    GodanI: [
        {"pos_info": ["x"], "base": "書く", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "泳ぐ", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "ござる", "c_type_info": "x五段x"},
    ],
    GodanZ: [
        {"pos_info": ["x"], "base": "立つ", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "売る", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "歌う", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "行く", "c_type_info": "x五段x"},
    ],
    GodanN: [
        {"pos_info": ["x"], "base": "死ぬ", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "遊ぶ", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "読む", "c_type_info": "x五段x"},
    ],
    GodanU: [
        {"pos_info": ["x"], "base": "問う", "c_type_info": "x五段x"},
        {"pos_info": ["x"], "base": "請う", "c_type_info": "x五段x"},
    ],
    Ichidan: [
        {"pos_info": ["x"], "base": "x", "c_type_info": "x一段x"},
    ],
    Kahen: [
        {"pos_info": ["x"], "base": "x", "c_type_info": "xカx変x"},
    ],
    Sahen: [
        {"pos_info": ["x"], "base": "x", "c_type_info": "xサx変x"},
    ],
    Adjective: [
        {"pos_info": ["形容詞"], "base": "x", "c_type_info": "x"},
    ],
    AuxiliaryDa: [
        {"pos_info": ["助動詞"], "base": "だ", "c_type_info": "x"},
    ],
    AuxiliaryNai: [
        {"pos_info": ["助動詞"], "base": "ない", "c_type_info": "x"},
    ],
    Nothing: [
        {"pos_info": ["x"], "base": "x", "c_type_info": ""},
    ],
    Unknown: [
        {"pos_info": ["x"], "base": "x", "c_type_info": "x"},
    ],
}


@pytest.mark.parametrize("ctype", ALL_CTYPE)
@pytest.mark.parametrize("ctype_, info_list", examples.items())
def test_conforms_to(
    ctype: Type[ConjugationType],
    ctype_: Type[ConjugationType],
    info_list: List[Dict[str, str]],
):
    if ctype == ctype_:
        expect = True
    elif ctype == Godan and ctype_ in (GodanI, GodanZ, GodanN, GodanU):
        expect = True
    else:
        expect = False
    for info in info_list:
        pos_info = info["pos_info"]
        base = info["base"]
        c_type_info = info["c_type_info"]
        err_msg = (ctype.__name__, ctype_.__name__, str(info))
        assert ctype.conforms_to(pos_info, base, c_type_info) == expect, err_msg


@pytest.mark.parametrize(
    "ctype, base, ending, expect",
    [
        (Godan, "晒す", "a", "晒さ"),
        (Godan, "書く", "い", "書い"),
        (GodanI, "書く", "oう", "書こう"),
        (GodanZ, "立つ", "i", "立ち"),
        (GodanN, "読む", "u", "読む"),
        (GodanU, "問う", "e", "問え"),
        (Ichidan, "食べる", "よう", "食べよう"),
        (Kahen, "くる", "こ", "こ"),
        (Kahen, "やってくる", "き", "やってき"),
        (Kahen, "来る", "こ", "来"),
        (Kahen, "やって来る", "こ", "やって来"),
        (Sahen, "する", "しよう", "しよう"),
        (Sahen, "読書する", "しよう", "読書しよう"),
        (Sahen, "論ずる", "すれ", "論ずれ"),
        (Adjective, "楽しい", "かろう", "楽しかろう"),
        (AuxiliaryDa, "だ", "だっ", "だっ"),
        (AuxiliaryNai, "ない", "かっ", "なかっ"),
    ],
)
def test_conjugate(ctype: Type[ConjugationType], base: str, ending: str, expect: str):
    assert ctype.conjugate(base, ending) == expect


@pytest.mark.parametrize(
    "ctype",
    [
        Nothing,
        Unknown,
    ],
)
def test_conjugate_invalid_ctype(ctype: Type[ConjugationType]):
    with pytest.raises(CannotConjugateError):
        ctype.conjugate("x", "x")


@pytest.mark.parametrize("ctype, info_list", examples.items())
def test_should_get_ctype(
    ctype: Type[ConjugationType], info_list: List[Dict[str, str]]
):
    for info in info_list:
        pos_info = info["pos_info"]
        base = info["base"]
        c_type_info = info["c_type_info"]
        ctype_ = get_normalized_ctype(pos_info, base, c_type_info)
        assert type(ctype_) == ctype
        assert ctype_.value == c_type_info
