from typing import ByteString

from tivars.data import String
from .tokens.scripts import *


with open("tivars/tokenizer/tokens/8X.xml", encoding="UTF-8") as file:
    ALL_8X = Tokens.from_xml_string(file.read())


def decode(bytestream: ByteString, *,
           tokens: Tokens = None, lang: str = "en",
           mode: str = "display") -> tuple[str | bytes, OsVersion]:
    tokens = tokens or ALL_8X

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


def encode(string: str, *, tokens: Tokens = None, lang: str = "en") -> tuple[bytes, OsVersion]:
    tokens = tokens or ALL_8X

    data = b''
    since = OsVersions.INITIAL
    max_length = max(map(len, tokens.langs[lang].keys()))

    index = 0
    while index < len(string):
        length = min(len(string), max_length)

        while length <= max_length:
            substring = string[index:][:length]
            if substring in tokens.langs[lang]:
                data += tokens.langs[lang][substring]

                since = max(tokens.bytes[tokens.langs[lang][substring]].since, since)

                index += length - 1
                break

            length -= 1

        else:
            raise ValueError(f"could not tokenize input at position {index}: '{string[index:][:max_length]}'")

        index += 1

    return data, since


class TokenizedString(String):
    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        return decode(data.ljust(8, b'\x00'))[0]

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        return encode(value)[0].rstrip(b'\x00')


__all__ = ["decode", "encode", "TokenizedString",
           "Tokens", "OsVersion", "OsVersions",
           "ALL_8X"]
