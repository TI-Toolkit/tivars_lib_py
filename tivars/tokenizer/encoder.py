"""
Context-aware text encoder
"""


import re
import unicodedata

from typing import Sequence

from tivars.models import *
from tivars.token import *
from tivars.trie import *
from tivars.util import *
from .state import *


def normalize(string: str):
    """
    Applies NFC normalization to a given string to ensure recognition of certain Unicode characters used as token names

    :param string: The text to normalize
    :return: The text in ``string`` normalized
    """

    return re.sub("[\u0398\u03F4\u1DBF]", "θ", unicodedata.normalize("NFC", string))


# Yucky scope nonsense to avoid a globals() call
_normalize = normalize


def tokenize(string: str, *, trie: TITokenTrie = None, mode: str = None, normalize: bool = True) -> list[TIToken]:
    r"""
    Tokenizes a string of tokens represented as text into a list of `TIToken` objects

    Tokenization is performed using one of three procedures, dictated by ``mode``:
        - ``max``: Always munch maximally, i.e. consume the most input possible to produce a token
        - ``smart``: Munch maximally or minimally depending on context
        - ``min``: Always munch minimally (equivalent to ``smart`` string context; may also be passed as ``string``)

    The ``smart`` tokenization mode uses the following contexts, munching maximally otherwise:
        - Strings: munch minimally, except when interpolating using ``Send(`` or storing to an equation
        - Program names: munch minimally up to 8 tokens
        - List names: munch minimally up to 5 tokens

    In all modes:
        - Standard glyphs can be used for substituting Unicode symbols
        - `\xXX` and `\uUUUU` output the denoted bytes exactly, regardless of validity
        - `\ABCD` maximally munches `ABCD`, regardless of surrounding context
        - Certain unprintable characters act as a hard separator for tokens
            - U+001F (unit separator): `␟`
            - U+200A (hair space): ` `
            - U+200C (zero width non-joiner): `‌`

    For reference, here are the tokenization modes utilized by popular IDEs and other software:
        - SourceCoder: ``max``
        - TokenIDE: ``max``
        - TI Connect CE: ¯\_(ツ)_/¯
        - TI-Planet Project Builder: ``smart``
        - tivars_lib_cpp: ``smart``

    :param string: The text string to encode
    :param trie: The `TokenTrie` object to use for tokenization (defaults to the TI-84+CE trie)
    :param mode: The tokenization mode to use (defaults to ``smart``)
    :param normalize: Whether to apply NFC normalization to the input before encoding (defaults to ``true``)
    :return: A list of `TIToken` objects represented by `string`
    """

    string = _normalize(string) if normalize else string
    trie = trie or TI_84PCE.tokens.tries[None]
    mode = mode or "smart"

    match mode:
        case "max":
            steps = [([], string, 0, [MaxMode()])]

        case "min" | "string":
            steps = [([], string, 0, [MinMode()])]

        case "smart":
            steps = [([], string, 0, [SmartMode()])]

        case _:
            raise ValueError(f"unrecognized tokenization mode: '{mode}'")

    while steps:
        tokens, string, index, stack = steps.pop(0)

        try:
            state = stack.pop()
            if not string:
                if state.accept:
                    return tokens

                else:
                    continue

            if isinstance(state, IllegalState):
                continue

        except IndexError:
            raise ValueError(f"stack consumed at position {index}: '{trim_string(string, 12)}'")

        try:
            token, remainder, timelines = state.munch(string, trie)
            for contexts in timelines:
                steps.append((tokens + [token], remainder, index + len(string) - len(remainder), stack + contexts))

        except (IndexError, ValueError):
            raise ValueError(f"failed to tokenize input at position {index}: '{trim_string(string, 12)}'")

    raise ValueError(f"all tokenization attempts failed; last segment was '{trim_string(string, 12)}'")


def unparse(tokens: Sequence[TIToken]) -> bytes:
    """
    Concatenates a `TIToken` sequence into a bytestream

    :param tokens: The tokens to encode
    :return: The bytes comprising `tokens`
    """

    return b"".join(token.bits for token in tokens)


def encode(string: str, *, model: TIModel = TI_84PCE, lang: str = None, mode: str = None) -> bytes:
    """
    Encodes a string of token represented as text into a byte stream

    For detailed information on tokenization modes, see `tivars.tokenizer.tokenize`.

    :param string: The text string to encode
    :param model: A model to target when encoding (defaults to no specific model)
    :param lang: The language used in `string` (defaults to the locale of `model`, or English, ``en``)
    :param mode: The tokenization mode to use (defaults to ``smart``)
    :return: The bytes comprising the tokens represented by `string`
    """

    return unparse(tokenize(string, trie=model.tokens.tries[lang or model.lang], mode=mode))


__all__ = ["normalize", "tokenize", "unparse", "encode"]
