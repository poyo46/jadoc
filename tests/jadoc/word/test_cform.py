from typing import Dict, List, Type

import pytest

from jadoc.word.cform import (
    ALL_CFORM,
    ConjugationForm,
    IshiSuiryo,
    Katei,
    Meirei,
    Mizen,
    Nothing,
    Rentai,
    Renyo,
    RenyoNi,
    RenyoOnbin,
    Shushi,
    Unknown,
    get_normalized_cform,
)

examples: Dict[Type[ConjugationForm], List[Dict[str, str]]] = {
    Mizen: [{"surface": "x", "c_form_info": "x未然x"}],
    IshiSuiryo: [
        {"surface": "x", "c_form_info": "x意志推量x"},
        {"surface": "x", "c_form_info": "x未然ウ接続x"},
        {"surface": "だろ", "c_form_info": "未然形"},
        {"surface": "でしょ", "c_form_info": "未然形"},
    ],
    Renyo: [
        {"surface": "x", "c_form_info": "x連用x"},
    ],
    RenyoOnbin: [
        {"surface": "x", "c_form_info": "x連用x音便x"},
        {"surface": "x", "c_form_info": "x連用タ接続x"},
    ],
    RenyoNi: [
        {"surface": "x", "c_form_info": "x連用xニx"},
    ],
    Shushi: [
        {"surface": "x", "c_form_info": "x終止x"},
        {"surface": "x", "c_form_info": "x基本x"},
    ],
    Rentai: [
        {"surface": "x", "c_form_info": "x連体x"},
        {"surface": "x", "c_form_info": "x体言接続x"},
    ],
    Katei: [
        {"surface": "x", "c_form_info": "x仮定x"},
    ],
    Meirei: [
        {"surface": "x", "c_form_info": "x命令x"},
    ],
    Nothing: [
        {"surface": "x", "c_form_info": ""},
    ],
    Unknown: [
        {"surface": "x", "c_form_info": "x"},
    ],
}


@pytest.mark.parametrize("cform", ALL_CFORM)
@pytest.mark.parametrize("cform_, info_list", examples.items())
def test_conforms_to(
    cform: Type[ConjugationForm],
    cform_: Type[ConjugationForm],
    info_list: List[Dict[str, str]],
):
    if cform == cform_:
        expect = True
    elif cform == Renyo and cform_ in (RenyoOnbin, RenyoNi):
        expect = True
    else:
        expect = False
    for info in info_list:
        surface = info["surface"]
        c_form_info = info["c_form_info"]
        err_msg = (cform.__name__, cform_.__name__, str(info))
        assert cform.conforms_to(surface, c_form_info) == expect, err_msg


@pytest.mark.parametrize("cform, info_list", examples.items())
def test_get_normalized_cform(
    cform: Type[ConjugationForm], info_list: List[Dict[str, str]]
):
    for info in info_list:
        surface = info["surface"]
        c_form_info = info["c_form_info"]
        cform_ = get_normalized_cform(surface, c_form_info)
        assert type(cform_) == cform
        assert cform_.value == c_form_info
