"""
Token stream decoder
"""


from warnings import warn

from tivars.models import *
from tivars.tokens.scripts import *


def invalid_token(bits: bytes) -> Token:
    name = rf"\x{bits.hex()}" if len(bits) == 1 else rf"\u{bits.hex()}"
    return Token(bits, {"en": Translation(b'?', "?", name, [])})



def decode(bytestream: bytes, *, tokens: Tokens = None) -> tuple[list[Token], OsVersion]:
    """
    Decodes a byte stream into a list of `Token` objects and its minimum supported OS version

    Each token is represented using one of three different representations formats, dictated by ``mode``:
        - ``display``: Represents the tokens with Unicode characters matching the calculator's display
        - ``accessible``: Represents the tokens with ASCII-only equivalents, often requiring multi-character glyphs
        - ``ti_ascii``: Represents the tokens with their internal font indices (returns a ``bytes`` object)

    :param bytestream: The token bytes to decode
    :param tokens: The `Tokens` object to use for decoding (defaults to the TI-84+CE tokens)
    :return: A tuple of a list of `Token` objects and a minimum `OsVersion`
    """

    tokens = tokens or TI_84PCE.tokens

    out = []
    since = OsVersions.INITIAL

    index = 0
    curr_bytes = b''
    while index < len(bytestream):
        curr_bytes += bytestream[index:][:1]
        curr_hex = curr_bytes.hex()

        if curr_bytes[0]:
            if curr_bytes in tokens.bytes:
                out.append(tokens.bytes[curr_bytes])
                since = max(tokens.bytes[curr_bytes].since, since)

                curr_bytes = b''

            elif len(curr_bytes) >= 2:
                warn(f"Unrecognized byte(s) '0x{curr_hex}' at position {index}.",
                     BytesWarning)

                out.append(invalid_token(curr_bytes))
                curr_bytes = b''

        elif curr_bytes[-1]:
            count = 0
            while not curr_bytes[0]:
                curr_bytes = curr_bytes[1:]
                count += 1
                out.append(invalid_token(b'\x00'))

            warn(f"There are {count} unexpected null bytes at position {index}." if count > 1 else
                 f"There is an unexpected null byte at position {index}.",
                 BytesWarning)

            curr_bytes = b''
            index -= 1

        index += 1

    return out, since


__all__ = ["decode"]
