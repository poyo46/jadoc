from typing import List

import pytest

from jadoc.cform import Mizen, Renyo
from jadoc.conj import Conjugation
from jadoc.doc import Doc


@pytest.fixture(scope="module")
def conjugations(request) -> List[Conjugation]:
    tokenizers = request.getfixturevalue("tokenizers")
    return [Conjugation(tokenize) for tokenize in tokenizers]


SURFACES = ["毎日", "とても", "歩き", "ます", "。"]
TEXT = "".join(SURFACES)


class TestDoc:
    def test_should_be_able_to_initialize_with_only_a_string(self):
        doc = Doc(TEXT)
        assert doc is not None

    def test_should_be_able_to_initialize_with_string(self, conjugations):
        for conjugation in conjugations:
            doc = Doc(TEXT, conjugation)
            surfaces = [word.surface for word in doc.words]
            assert surfaces == SURFACES

    def test_should_be_able_to_initialize_with_word_list(self, conjugations):
        for conjugation in conjugations:
            words = conjugation.tokenize(TEXT)
            doc = Doc(words, conjugation)
            surfaces = [word.surface for word in doc.words]
            assert surfaces == SURFACES

    @pytest.mark.parametrize(
        "interval, expect",
        [(None, TEXT), (1, SURFACES[1]), (range(1, 3), "".join(SURFACES[1:3]))],
    )
    def test_should_be_able_to_extract_text(self, conjugations, interval, expect):
        for conjugation in conjugations:
            doc = Doc(TEXT, conjugation)
            assert doc.text(interval) == expect

    @pytest.mark.parametrize(
        "text, i, cform, expect",
        [
            (TEXT, -1, Mizen, TEXT),
            ("そうでありない", 2, Mizen, "そうでない"),
            ("そうするれる", 1, Mizen, "そうされる"),
            ("そうするぬ", 1, Mizen, "そうせぬ"),
            ("そうするない", 1, Mizen, "そうしない"),
            ("本を読むない", 2, Mizen, "本を読まない"),
            ("本を読むた", 2, Renyo, "本を読んだ"),
            ("本を書くだ", 2, Renyo, "本を書いた"),
        ],
    )
    def test_conjugate_word_in_doc(self, conjugations, text, i, cform, expect):
        for conjugation in conjugations:
            doc = Doc(text, conjugation)
            doc.conjugate(i, cform)
            assert doc.text() == expect

    def test_insert_a_single_word(self, conjugations):
        for conjugation in conjugations:
            doc = Doc(TEXT, conjugation)
            text = "公園"
            word = conjugation.tokenize(text)[0]
            doc.insert(1, word)
            assert doc.text() == SURFACES[0] + text + "".join(SURFACES[1:])

    @pytest.mark.parametrize(
        "text, surfaces, i, expect",
        [
            (TEXT, "あの公園を", 1, SURFACES[0] + "あの公園を" + "".join(SURFACES[1:])),
            ("毎日とても歩きます。", "だり、音楽を聞く", 3, "毎日とても歩いたり、音楽を聞きます。"),
        ],
    )
    def test_insert(self, conjugations, text, surfaces, i, expect):
        for conjugation in conjugations:
            doc = Doc(text, conjugation)
            words = conjugation.tokenize(surfaces)
            doc.insert(i, words)
            assert doc.text() == expect

    def test_insert_after_word_whose_cform_is_unknown(self, conjugations):
        for conjugation in conjugations:
            doc = Doc(TEXT, conjugation)
            doc.words[0].c_form = "x"
            doc.insert(1, [])
            assert doc.text() == TEXT

    @pytest.mark.parametrize(
        "text, interval, expect",
        [
            (TEXT, range(-10, 10), TEXT),
            (TEXT, 0, "".join(SURFACES[1:])),
            ("本を書きました", range(3, 4), "本を書いた"),
            ("本を書きました", 1, "本書きました"),
        ],
    )
    def test_delete(self, conjugations, text, interval, expect):
        for conjugation in conjugations:
            doc = Doc(text, conjugation)
            doc.delete(interval)
            assert doc.text() == expect

    def test_delete_word_whose_cform_is_unknown(self, conjugations):
        for conjugation in conjugations:
            doc = Doc(TEXT, conjugation)
            doc.words[0].c_form = "x"
            doc.delete(0)
            assert doc.text() == "".join(SURFACES[1:])

    def test_update_a_single_word(self, conjugations):
        for conjugation in conjugations:
            doc = Doc(TEXT, conjugation)
            text = "毎週"
            word = conjugation.tokenize(text)[0]
            doc.update(0, word)
            assert doc.text() == "毎週" + "".join(SURFACES[1:])

    @pytest.mark.parametrize(
        "text, interval, surfaces, expect",
        [
            (TEXT, 0, "毎週", "毎週" + "".join(SURFACES[1:])),
            (TEXT, range(-10, 10), "毎週", TEXT),
            ("本を書きました。", range(2, 4), "読む", "本を読んだ。"),
            (TEXT, range(2, 4), "走っ", "毎日とても走る。"),
        ],
    )
    def test_update(self, conjugations, text, interval, surfaces, expect):
        for conjugation in conjugations:
            doc = Doc(text, conjugation)
            words = conjugation.tokenize(surfaces)
            doc.update(interval, words)
            assert doc.text() == expect

    @pytest.mark.parametrize(
        "text, interval, surfaces, expect",
        [
            (TEXT, 0, "毎週", "毎週" + "".join(SURFACES[1:])),
            (TEXT, range(-10, 10), "毎週", TEXT),
            (TEXT, range(0, 2), "毎週かなり", "毎週かなり" + "".join(SURFACES[2:])),
            (TEXT, range(0, 2), ["毎週", "かなり"], "毎週かなり" + "".join(SURFACES[2:])),
        ],
    )
    def test_update_surfaces(self, conjugations, text, interval, surfaces, expect):
        for conjugation in conjugations:
            doc = Doc(text, conjugation)
            doc.update_surfaces(interval, surfaces)
            assert doc.text() == expect

    def test_copy(self, conjugations):
        for conjugation in conjugations:
            doc = Doc("こんにちは。", conjugation)
            copied_doc = doc.copy()
            assert id(doc) != id(copied_doc)
            assert id(doc.words) != id(copied_doc.words)
            for word_org, word_copy in zip(doc.words, copied_doc.words):
                assert word_org.to_dict() == word_copy.to_dict()
