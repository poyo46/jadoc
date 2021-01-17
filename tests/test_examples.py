from jadoc.doc import Doc


def test():
    doc = Doc("本を書きました。")

    # print surface forms of the tokens.
    surfaces = [word.surface for word in doc.words]
    print("/".join(surfaces))  # 本/を/書き/まし/た/。

    # print plain text
    print(doc.get_text())  # 本を書きました。

    # delete a word
    doc.delete(3)  # Word conjugation will be done as needed.
    print(doc.get_text())  # 本を書いた。

    # update a word
    word = doc.conjugation.tokenize("読む")
    # In addition to conjugation, transform the peripheral words as needed.
    doc.update(2, word)
    print(doc.get_text())  # 本を読んだ。
