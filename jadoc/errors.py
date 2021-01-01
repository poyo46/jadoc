class JadocError(Exception):
    """
    Base class for exceptions in this module.
    """

    pass


class UnknownPosError(JadocError):
    """
    Raised when part of speech is unknown.
    """

    pass


class UnknownCTypeError(JadocError):
    """
    Raised when conjugation type is unknown.
    """

    pass


class UnknownCFormError(JadocError):
    """
    Raised when conjugation form is unknown.
    """

    pass


class UnknownConjugationError(JadocError):
    """
    Raised when conjugation is unknown.
    """

    pass
