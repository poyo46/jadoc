class JadocError(Exception):
    """
    Base class for exceptions in this module.
    """

    pass


class CannotConjugateError(JadocError):
    """
    Raised when a word with no conjugation is conjugated.
    """

    pass


class MecabConfigError(JadocError):
    """
    Raised when the ``mecab-config`` command is not found.
    """

    pass


class NotFoundNodeFormatError(JadocError):
    """
    Raised when the MeCab ``node-format`` could not be set automatically.
    """

    pass


class InvalidTokenizerError(JadocError):
    """
    Raised when the tokenizer is not working properly.
    """

    pass
