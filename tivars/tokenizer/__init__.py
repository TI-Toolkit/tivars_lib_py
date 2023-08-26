from typing import ByteString

from tivars.data import String
from ..models import *
from .tokens.scripts import *


def decode(bytestream: ByteString, *,
           tokens: Tokens = None, lang: str = "en",
           mode: str = "display") -> tuple[str | bytes, OsVersion]:
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

        index += 1

    return b''.join(out) if mode == "ti_ascii" else "".join(out), since


def encode(string: str, trie: TokenTrie) -> tuple[bytes, OsVersion]:
    data = b''
    since = OsVersions.INITIAL
    index = 0

    while string:
        token, remainder = trie.get_longest_token(string)

        if token is None:
            raise ValueError(f"could not tokenize input at position {index}: '{string[:12]}'")

        data += token.bits
        since = max(token.since, since)

        index += len(string) - len(remainder)
        string = remainder

    return data, since


class TokenizedString(String):
    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        return decode(data.ljust(8, b'\x00'))[0]

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        return encode(value, TI_84PCE.get_trie())[0].rstrip(b'\x00')


__all__ = ["decode", "encode", "TokenizedString",
           "Tokens", "OsVersion", "OsVersions"]
