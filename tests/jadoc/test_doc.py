import pytest

from jadoc.conj import Conjugation
from jadoc.doc import Doc
from jadoc.mecab.config import get_dicdirs
from jadoc.mecab.tokenizer import generate_tokenizer
from jadoc.word.cform import Mizen, Renyo

conjugations = [Conjugation(generate_tokenizer(dicdir)) for dicdir in get_dicdirs()]


SURFACES = ["毎日", "とても", "歩き", "ます", "。"]
TEXT = "".join(SURFACES)


class TestDoc:
    def test_should_be_able_to_initialize_with_only_a_string(self):
        doc = Doc(TEXT)
        assert doc is not None

    @pytest.mark.parametrize("conjugation", conjugations)
    def test_should_be_able_to_initialize_with_string(self, conjugation):
        doc = Doc(TEXT, conjugation)
        surfaces = [word.surface for word in doc.words]
        assert surfaces == SURFACES

    @pytest.mark.parametrize("conjugation", conjugations)
    @pytest.mark.parametrize(
        "interval, expect",
        [(None, TEXT), (1, SURFACES[1]), (range(1, 3), "".join(SURFACES[1:3]))],
    )
    def test_should_be_able_to_extract_text(self, conjugation, interval, expect):
        doc = Doc(TEXT, conjugation)
        assert doc.get_text(interval) == expect

    @pytest.mark.parametrize("conjugation", conjugations)
    def test_retokenize(self, conjugation):
        doc = Doc(TEXT, conjugation)
        doc.retokenize()
        assert doc.get_text() == TEXT
        text = "今日はいい天気ですね。"
        doc.retokenize(text)
        assert doc.get_text() == text

    @pytest.mark.parametrize("conjugation", [conjugations[0]])
    @pytest.mark.parametrize(
        "text, i, c_form, expect",
        [
            (TEXT, -1, Mizen("未然形"), TEXT),
            ("そうでありない", 2, Mizen("未然形"), "そうでない"),
            ("そうするれる", 1, Mizen("未然形"), "そうされる"),
            ("そうするぬ", 1, Mizen("未然形"), "そうせぬ"),
            ("そうする", 1, Mizen("未然形"), "そうし"),
            ("そうするない", 1, Mizen("未然形"), "そうしない"),
            ("本を読むない", 2, Mizen("未然形"), "本を読まない"),
            ("本を読むた", 2, Renyo("連用形"), "本を読んだ"),
            ("本を書くだ", 2, Renyo("連用形"), "本を書いた"),
        ],
    )
    def test_conjugate_word_in_doc(self, conjugation, text, i, c_form, expect):
        doc = Doc(text, conjugation)
        doc.conjugate(i, c_form)
        assert doc.get_text() == expect

    @pytest.mark.parametrize("conjugation", conjugations)
    def test_insert_a_single_word(self, conjugation):
        doc = Doc(TEXT, conjugation)
        text = "公園"
        word = conjugation.tokenize(text)[0]
        doc.insert(1, word)
        assert doc.get_text() == SURFACES[0] + text + "".join(SURFACES[1:])

    @pytest.mark.parametrize("conjugation", conjugations)
    @pytest.mark.parametrize(
        "text, surfaces, i, expect",
        [
            (TEXT, "私は", 0, "私は" + TEXT),
            (TEXT, "あの公園を", 1, SURFACES[0] + "あの公園を" + "".join(SURFACES[1:])),
            ("毎日とても歩きます。", "だり、音楽を聞く", 3, "毎日とても歩いたり、音楽を聞きます。"),
        ],
    )
    def test_insert(self, conjugation, text, surfaces, i, expect):
        doc = Doc(text, conjugation)
        words = conjugation.tokenize(surfaces)
        doc.insert(i, words)
        assert doc.get_text() == expect

    @pytest.mark.parametrize("conjugation", conjugations)
    @pytest.mark.parametrize(
        "text, interval, expect",
        [
            (TEXT, range(-10, 10), TEXT),
            (TEXT, 0, "".join(SURFACES[1:])),
            ("本を書きました", range(3, 4), "本を書いた"),
            ("本を書きました", 1, "本書きました"),
        ],
    )
    def test_delete(self, conjugation, text, interval, expect):
        doc = Doc(text, conjugation)
        doc.delete(interval)
        assert doc.get_text() == expect

    @pytest.mark.parametrize("conjugation", conjugations)
    def test_update_a_single_word(self, conjugation):
        doc = Doc(TEXT, conjugation)
        text = "毎週"
        word = conjugation.tokenize(text)[0]
        doc.update(0, word)
        assert doc.get_text() == "毎週" + "".join(SURFACES[1:])

    @pytest.mark.parametrize("conjugation", conjugations)
    @pytest.mark.parametrize(
        "text, interval, surfaces, expect",
        [
            (TEXT, 0, "毎週", "毎週" + "".join(SURFACES[1:])),
            (TEXT, range(-10, 10), "毎週", TEXT),
            ("本を書きました。", range(2, 4), "読む", "本を読んだ。"),
            (TEXT, range(2, 4), "走っ", "毎日とても走る。"),
        ],
    )
    def test_update(self, conjugation, text, interval, surfaces, expect):
        doc = Doc(text, conjugation)
        words = conjugation.tokenize(surfaces)
        doc.update(interval, words)
        assert doc.get_text() == expect

    @pytest.mark.parametrize("conjugation", conjugations)
    @pytest.mark.parametrize(
        "text, interval, surfaces, expect",
        [
            (TEXT, 0, "毎週", "毎週" + "".join(SURFACES[1:])),
            (TEXT, range(-10, 10), "毎週", TEXT),
            (TEXT, range(0, 2), "毎週かなり", "毎週かなり" + "".join(SURFACES[2:])),
            (TEXT, range(0, 2), ["毎週", "かなり"], "毎週かなり" + "".join(SURFACES[2:])),
        ],
    )
    def test_update_surfaces(self, conjugation, text, interval, surfaces, expect):
        doc = Doc(text, conjugation)
        doc.update_surfaces(interval, surfaces)
        assert doc.get_text() == expect

    def test_simple_view(self):
        doc = Doc(TEXT)
        assert len(doc.simple_view()) > 0

    def test_to_word_list(self):
        doc = Doc(TEXT)
        for dic in doc.to_word_list():
            assert type(dic) == dict
