"""
Tokenization utilities derived from the token sheets (see tokens directory)
"""


from warnings import warn

from tivars.data import String
from tivars.models import *
from tivars.token import *
from tivars.tokens.scripts import *
from tivars.trie import *
from .decoder import *
from .encoder import *


class TokenizedString(String):
    """
    Converter for data sections best interpreted as strings of tokens

    Tokenization uses the TI-84+CE token sheet.
    """

    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        return "".join(token.langs["en"].display for token in decode(data.ljust(8, b'\x00'))[0])

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        return encode(value)[0].rstrip(b'\x00')


class Name(TokenizedString):
    """
    Converter for names of vars

    Tokenization uses the TI-84+CE token sheet, which is backwards compatible for all var name tokens.
    """

    _T = str

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        # Is this necessary?
        mode = "max" if instance is not None and instance.leading_name_byte else "string"
        data = encode(value, mode=mode)[0].rstrip(b'\x00')

        if instance is not None and not data.startswith(instance.leading_name_byte):
            warn(f"Entry has an invalid name: '{value}'.",
                 BytesWarning)

        return data


__all__ = ["decode", "encode", "normalize", "Name", "TokenizedString",
           "TIToken", "IllegalToken", "TITokenTrie", "TITokens", "OsVersion", "OsVersions"]
