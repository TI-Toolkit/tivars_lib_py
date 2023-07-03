from typing import ByteString

from tivars.data import String
from .parse import *
from .tokens import *


def decode(bytestream: ByteString, byte_map: ByteMap) -> str:
    string = ""
    index = 0
    curr_bytes = b''
    while index < len(bytestream):
        curr_bytes += bytestream[index].to_bytes(1, 'little')
        if curr_bytes in byte_map:
            string += byte_map[curr_bytes][0]
            curr_bytes = b''

        elif len(curr_bytes) == 2:
            if not any(key.startswith(curr_bytes[:1]) for key in byte_map):
                raise ValueError(f"unrecognized byte '0x{curr_bytes[0]:x}' at position {index}")

            else:
                raise ValueError(f"unrecognized bytes '0x{curr_bytes[0]:x}{curr_bytes[1]:x}' at position {index}")

        index += 1

    return string


def encode(string: str, token_map: TokenMap) -> bytes:
    data = b''
    max_length = max(map(len, token_map.keys()))
    within_string = False

    index = 0
    while index < len(string):
        if within_string:
            length = 1
            direction = 1
        else:
            length = min(len(string), max_length)
            direction = -1

        while length <= max_length if within_string else length > 0:
            substring = string[index:][:length]
            if substring in token_map:
                value = token_map[substring].bytes
                data += value

                if substring == '"':
                    within_string = not within_string
                elif token_map[substring].terminator:
                    within_string = False

                index += length - 1
                break

            length += direction

        else:
            raise ValueError(f"Could not tokenize input at position {index}: '{string[index:][:max_length]}'.")

        index += 1

    return data


class TokenizedString(String):
    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        return decode(data.ljust(8, b'\x00'), CE_BYTES)

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        return encode(value, CE_TOKENS).rstrip(b'\x00')


__all__ = ["decode", "encode", "load_tokens_xml", "TokenizedString",
           "AXE_TOKENS", "CE_TOKENS", "CSE_TOKENS", "GRAMMER_TOKENS",
           "TI83_TOKENS", "PRIZM_TOKENS", "TI82_TOKENS", "TI73_TOKENS",
           "AXE_BYTES", "CE_BYTES", "CSE_BYTES", "GRAMMER_BYTES",
           "TI83_BYTES", "PRIZM_BYTES", "TI82_BYTES", "TI73_BYTES"]
