"""
Context-aware text encoder
"""


from tivars.models import *
from tivars.tokens.scripts import *
from .state import *


def encode(string: str, *,
           trie: TokenTrie = None, mode: str = "smart") -> tuple[bytes, OsVersion]:
    """
    Encodes a string of token represented in text into a byte stream and its minimum supported OS version

    Tokenization is performed using one of three procedures, dictated by ``mode``:
        - ``max``: Always munch maximally, i.e. consume the most input possible to produce a token
        - ``smart``: Munch maximally or minimally depending on context
        - ``string``: Always munch minimally (equivalent to ``smart`` string context)

    The ``smart`` tokenization mode uses the following contexts, munching maximally otherwise:
        - Strings: munch minimally, except when interpolating using ``Get(``/``Send(``
        - Program names: munch minimally up to 8 tokens
        - List names: munch minimally up to 5 tokens

    For reference, here are the tokenization modes utilized by popular IDEs and other software:
        - SourceCoder: ``max``
        - TokenIDE: ``max``
        - TI Connect CE: ``smart``
        - TI-Planet Project Builder: ``smart``
        - tivars_lib_cpp: ``smart``

    All tokenization modes respect token glyphs for substituting Unicode symbols.

    :param string: The text string to encode
    :param trie: The `TokenTrie` object to use for tokenization
    :param mode: The tokenization mode to use (defaults to ``smart``)
    :return: A tuple of a stream of token bytes and a minimum `OsVersion`
    """

    trie = trie or TI_84PCE.get_trie()

    data = b''
    since = OsVersions.INITIAL
    index = 0

    match mode:
        case "max":
            stack = [MaxMode()]

        case "smart":
            stack = [SmartMode()]

        case "string":
            stack = [MinMode()]

        case _:
            raise ValueError(f"unrecognized tokenization mode: '{mode}'")

    while string:
        try:
            token, remainder, contexts = stack.pop().munch(string, trie)
            stack += contexts

        except ValueError:
            raise ValueError(f"could not tokenize input at position {index}: '{string[:12]}'")

        except IndexError:
            raise ValueError(f"stack consumed at position {index}: '{string[:12]}'")

        data += token.bits
        since = max(token.since, since)

        index += len(string) - len(remainder)
        string = remainder

    return data, since


__all__ = ["encode"]
