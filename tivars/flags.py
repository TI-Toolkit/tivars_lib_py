from functools import total_ordering
from math import ceil
from typing import Mapping
from warnings import warn

from .data import *


class Enum(Converter):
    _T = bytes

    _all = []

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return bytes(data[0:1])

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        if value not in cls._all:
            warn(f"{value} is not recognized.",
                 BytesWarning)

        return value

    @classmethod
    def get_name(cls, value: _T) -> str:
        return next(filter(lambda attr: not attr.startswith("_") and getattr(cls, attr) == value, dir(cls)), None)


@total_ordering
class Flags(Converter, dict, Mapping[int, int]):
    _T = 'Flags'

    def __init__(self, bitsets: Mapping[int, int] | 'Flags' = None, *, width: int = 8):
        if bitsets is None:
            bitsets = {bit: 0 for bit in range(width)}

        else:
            bitsets = {bit: 0 for bit in range(ceil((max(bitsets.keys()) + 1) / 8) * 8)} | bitsets

        super().__init__({bit: value % 2 for bit, value in bitsets.items()})

    def __gt__(self, other) -> bool:
        return int(self) > int(other)

    def __int__(self) -> int:
        return int(str(self), 2)

    def __str__(self) -> str:
        return ''.join([str(bit) for bit in self.values()][::-1])

    def __contains__(self, bitsets: Mapping[int, int] | 'Flags') -> bool:
        return all(self[bit] == int(bool(bitsets[bit])) for bit in bitsets)

    has = __contains__

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return cls({bit: int(value) for bit, value in enumerate(f"{int.from_bytes(data, 'little'):b}"[::-1])})

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(int(value), len(value) // 8, 'little')


__all__ = ["Enum", "Flags"]
