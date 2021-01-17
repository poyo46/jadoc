from typing import Dict, List, Optional

from .cform import get_normalized_cform
from .ctype import Nothing, Unknown, get_normalized_ctype
from .pos import get_normalized_pos


class Word:
    def __init__(
        self,
        surface: str,
        pos_info: List[str],
        base: Optional[str] = None,
        c_type_info: Optional[str] = None,
        c_form_info: Optional[str] = None,
    ) -> None:
        self.surface = surface
        self.pos = get_normalized_pos(pos_info)

        if base is None or base == "":
            self.base = surface
        else:
            self.base = base

        if c_type_info is None:
            c_type_info = ""
        self.c_type = get_normalized_ctype(pos_info, self.base, c_type_info)

        if c_form_info is None:
            c_form_info = ""
        self.c_form = get_normalized_cform(surface, c_form_info)

        self.has_conjugation = (
            type(self.c_type) != Nothing and type(self.c_type) != Unknown
        )

    def to_dict(self) -> Dict[str, str]:
        """Convert this word to a ``dict`` object.

        Returns
        -------
        dict
            The attributes of this word.
        """
        return {
            "surface": self.surface,
            "pos": str(self.pos),
            "base": self.base,
            "c_type": str(self.c_type),
            "c_form": str(self.c_form),
            "has_conjugation": str(self.has_conjugation),
        }

    def __str__(self) -> str:
        """Represent this word as a string.

        Returns
        -------
        str
            A string representing the attributes of this word.
        """
        return str(self.to_dict())
