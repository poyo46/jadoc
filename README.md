# Jadoc: Tokenizes Japanese Documents to Enable CRUD Operations

[![PyPI Version](https://img.shields.io/pypi/v/jadoc.svg)](https://pypi.org/pypi/jadoc/)
[![Python Versions](https://img.shields.io/pypi/pyversions/jadoc.svg)](https://pypi.org/pypi/jadoc/)
[![License](https://img.shields.io/pypi/l/jadoc.svg)](https://github.com/poyo46/jadoc/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

## Installation

**Install MeCab**

MeCab is required for Jadoc to work.
If it is not already installed, [install MeCab](https://taku910.github.io/mecab/) first.

**Install Jadoc**

```console
$ pip install jadoc
```

## Examples

```python
from jadoc.doc import Doc


doc = Doc("本を書きました。")

# print surface forms of the tokens.
surfaces = [word.surface for word in doc.words]
print("/".join(surfaces))  # 本/を/書き/まし/た/。

# print plain text
print(doc.text())  # 本を書きました。

# delete a word
doc.delete(3)  # Word conjugation will be done as needed.
print(doc.text())  # 本を書いた。

# update a word
word = doc.conjugation.tokenize("読む")
# In addition to conjugation, transform the peripheral words as needed.
doc.update(2, word)
print(doc.text())  # 本を読んだ。
```
