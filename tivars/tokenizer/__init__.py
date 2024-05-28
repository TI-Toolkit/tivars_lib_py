"""
Tokenization utilities derived from the token sheets (see tokens directory)
"""


import re
from warnings import warn

from tivars.data import String
from tivars.models import *
from tivars.tokens.scripts import *
from .decoder import *
from .encoder import *


class TokenizedString(String):
    """
    Converter for data sections best interpreted as strings of tokens

    Tokenization uses the TI-84+CE token sheet, which is backwards compatible for all var name tokens.
    """

    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        return decode(data.ljust(8, b'\x00'))[0]

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        data = encode(re.sub(r"[\u0398\u03F4\u1DBF]", "θ", value), mode="string")[0].rstrip(b'\x00')

        if instance is not None and not data.startswith(instance.leading_name_byte):
            warn(f"Entry has an invalid name: '{value}'.",
                 BytesWarning)

        return data


__all__ = ["decode", "encode", "TokenizedString",
           "Tokens", "OsVersion", "OsVersions"]
