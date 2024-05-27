"""
Tokenization utilities derived from the token sheets (see tokens directory)
"""


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
    def set(cls, value: _T, **kwargs) -> bytes:
        return encode(value)[0].rstrip(b'\x00')


__all__ = ["decode", "encode", "TokenizedString",
           "Tokens", "OsVersion", "OsVersions"]
