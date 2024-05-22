"""
Tokenization utilities derived from the token sheets (see tokens directory)
"""


from tivars.data import String
from tivars.models import *
from tivars.tokens.scripts import *


STRING_STARTERS = b'\x2A'
"""
Token bytes which can start a string
"""

STRING_TERMINATORS = b'\x04\x2A\x3F'
"""
Token bytes which can end a string
"""


def decode(bytestream: bytes, *,
           tokens: Tokens = None, lang: str = "en",
           mode: str = "display") -> tuple[str | bytes, OsVersion]:
    """
    Decodes a byte stream into a string of tokens and its minimum supported OS version

    Each token is represented using one of three different representations formats, dictated by ``mode``:
        - ``display``: Represents the tokens with Unicode characters matching the calculator's display
        - ``accessible``: Represents the tokens with ASCII-only equivalents, often requiring multi-character glyphs
        - ``ti_ascii``: Represents the tokens with their internal font indices (returns a ``bytes`` object)

    :param bytestream: The bytes to decode
    :param tokens: The `Tokens` object to use for decoding
    :param lang: The language used in ``string`` (defaults to English, ``en``)
    :param mode: The form of token representation to use for output (defaults to ``display``)
    :return: A tuple of a string of token representations and a minimum `OsVersion`
    """

    tokens = tokens or TI_84PCE.tokens

    out = []
    since = OsVersions.INITIAL

    index = 0
    curr_bytes = b''
    while index < len(bytestream):
        curr_bytes += bytestream[index:][:1]

        if curr_bytes[0]:
            if curr_bytes in tokens.bytes:
                out.append(getattr(tokens.bytes[curr_bytes].langs[lang], mode))
                since = max(tokens.bytes[curr_bytes].since, since)

                curr_bytes = b''

            elif len(curr_bytes) >= 2:
                if not any(key.startswith(curr_bytes[:1]) for key in tokens.bytes):
                    raise ValueError(f"unrecognized byte '0x{curr_bytes[0]:x}' at position {index}")

                else:
                    raise ValueError(f"unrecognized bytes '0x{curr_bytes[0]:x}{curr_bytes[1]:x}' at position {index}")

        elif any(curr_bytes):
            raise ValueError(f"unexpected null byte at position {index}")

        index += 1

    return b''.join(out) if mode == "ti_ascii" else "".join(out), since


def encode(string: str, trie: TokenTrie, mode: str = "max") -> tuple[bytes, OsVersion]:
    """
    Encodes a string of token represented in text into a byte stream and its minimum supported OS version

    Tokenization is performed using one of three procedures, dictated by ``mode``:
        - ``max``: Always munch maximally, i.e. consume the *longest* possible string to produce a token
        - ``min``: Always munch minimally, i.e. consume the *shortest* possible string to produce a token
        - ``minmax``: Munch maximally outside strings and minimally inside strings

    For reference, here are the tokenization modes utilized by popular IDEs and other software:
        - SourceCoder: ``max``
        - TokenIDE: ``max``
        - TI-Planet Project Builder: ``minmax``
        - tivars_lib_cpp: ``minmax``

    :param string: The tokens to encode
    :param trie: The `TokenTrie` object to use for tokenization
    :param mode: The tokenization mode to use (defaults to ``max``)
    :return: A tuple of a stream of token bytes and a minimum `OsVersion`
    """

    data = b''
    since = OsVersions.INITIAL
    index = 0
    in_string = False

    while string:
        match mode:
            case "max":
                token, remainder = trie.get_tokens(string)[0]

            case "min":
                token, remainder = trie.get_tokens(string)[-1]

            case "minmax" | "maxmin":
                token, remainder = trie.get_tokens(string)[-1 if in_string else 0]

            case _:
                raise ValueError(f"unrecognized tokenization mode: '{mode}'")

        if token is None:
            raise ValueError(f"could not tokenize input at position {index}: '{string[:12]}'")

        data += token.bits
        since = max(token.since, since)

        index += len(string) - len(remainder)
        string = remainder

        match in_string:
            case False if token.bits in STRING_STARTERS:
                in_string = True

            case True if token.bits in STRING_TERMINATORS:
                in_string = False

    return data, since


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
        return encode(value, TI_84PCE.get_trie())[0].rstrip(b'\x00')


__all__ = ["decode", "encode", "TokenizedString",
           "Tokens", "OsVersion", "OsVersions"]
