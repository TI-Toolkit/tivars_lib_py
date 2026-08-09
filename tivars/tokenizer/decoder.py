"""
Token stream decoder
"""


from typing import Sequence
from warnings import warn

from tivars.models import *
from tivars.token import *
from tivars.trie import *


def parse(bytestream: bytes, *, tokens: TITokens = None) -> list[TIToken]:
    """
    Parses a byte stream into a list of `TIToken` objects

    Each token is represented using one of three different representations formats, dictated by ``mode``:
        - ``display``: Represents the tokens with Unicode characters matching the calculator's display
        - ``accessible``: Represents the tokens with ASCII-only equivalents, often requiring multi-character glyphs
        - ``ti_ascii``: Represents the tokens with their internal font indices (returns a ``bytes`` object)

    :param bytestream: The token bytes to parse
    :param tokens: The `TITokens` object to use for decoding (defaults to the TI-84+CE tokens)
    :return: A list of `TIToken` objects assembled from `bytestream`
    """

    tokens = tokens or TI_84PCE.tokens

    out = []

    index = 0
    curr_bytes = b''
    while index < len(bytestream):
        curr_bytes += bytestream[index:][:1]
        curr_hex = curr_bytes.hex()

        if curr_bytes[0]:
            if curr_bytes in tokens.bytes:
                out.append(tokens.bytes[curr_bytes])

                curr_bytes = b''

            elif len(curr_bytes) >= 2:
                warn(f"Unrecognized byte(s) '0x{curr_hex}' at position {index}.",
                     BytesWarning)

                out.append(IllegalToken(curr_bytes))
                curr_bytes = b''

        elif curr_bytes[-1]:
            count = 0
            while not curr_bytes[0]:
                curr_bytes = curr_bytes[1:]
                count += 1
                out.append(IllegalToken(b'\x00'))

            warn(f"There are {count} unexpected null bytes at position {index}." if count > 1 else
                 f"There is an unexpected null byte at position {index}.",
                 BytesWarning)

            curr_bytes = b''
            index -= 1

        index += 1

    return out


def detokenize(tokens: Sequence[TIToken], *, model: TIModel = TI_84PCE, lang: str = None, mode: str = None):
    """
    Stringifies a sequence of `TIToken` objects given a language and token representation type

    :param tokens: The `TIToken` sequence to stringify
    :param model: The target model (defaults to the TI-84+CE)
    :param lang: The target language (defaults to the locale of `model`, or English, ``en``)
    :param mode: The token representation to use for output (defaults to ``display``)
    :return: A string representing `tokens`
    """

    try:
        return "".join(getattr(token.langs[lang or model.lang], mode or "display") for token in tokens)

    except (AttributeError, TypeError):
        raise ValueError(f"unrecognized token representation: '{mode}'")


def decode(data: bytes, *, model: TIModel = TI_84PCE, lang: str = None, mode: str = None) -> str:
    """
    Decodes a byte stream into a string of tokens

    :param data: The token bytes to decode
    :param model: A model for which compatibility is ensured (defaults to the TI-84+CE)
    :param lang: The language used in ``string`` (defaults to the locale of `model`, or English, ``en``)
    :param mode: The token representation to use for output (defaults to ``display``)
    :return: A string representing the tokens in `data`
    """

    return detokenize(parse(data, tokens=model.tokens), model=model, lang=lang, mode=mode)


__all__ = ["parse", "detokenize", "decode"]
