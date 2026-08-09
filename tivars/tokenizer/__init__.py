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

    @classmethod
    def get(cls, data: bytes, **kwargs) -> str:
        return decode(data.ljust(8, b'\x00'))

    @classmethod
    def set(cls, value: str, **kwargs) -> bytes:
        return encode(value).rstrip(b'\x00')


class Name(TokenizedString):
    """
    Converter for names of vars

    Tokenization uses the TI-84+CE token sheet, which is backwards compatible for all var name tokens.
    """

    @classmethod
    def set(cls, value: str, *, instance=None, **kwargs) -> bytes:
        data = super().set(value, **kwargs)

        if instance is not None and not data.startswith(instance.leading_name_byte):
            warn(f"Entry has an invalid name: '{value}'.",
                 BytesWarning)

        return data


__all__ = ["parse", "detokenize", "decode", "normalize", "tokenize", "unparse", "encode",
           "Name", "TokenizedString",
           "TIToken", "IllegalToken", "TITokenTrie", "TITokens", "OsVersion", "OsVersions"]
