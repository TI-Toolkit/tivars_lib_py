from collections.abc import Iterator
from functools import total_ordering
from warnings import warn

from .data import *


Bitsets = dict[int, int]


class Enum(Converter):
    _T = 'Enum'

    _all = []

    @classmethod
    def get(cls, data: bytes, instance) -> int:
        return data[0]

    @classmethod
    def set(cls, value: int, instance) -> bytes:
        if value not in cls._all:
            warn(f"{value} is not recognized.",
                 BytesWarning)

        return bytes([value])


@total_ordering
class Flags(Converter):
    _T = 'Flags'

    def __init__(self, bits):
        try:
            bits = f"{bits:b}"[::-1]

        except TypeError:
            pass

        except ValueError:
            bits = bits[::-1]

        self._bits = [int(bit) for bit in bits]

        if len(self._bits) % 8:
            self._bits += [0] * (8 - len(self._bits) % 8)

    def __eq__(self, other) -> bool:
        return int(self) == int(other)

    def __gt__(self, other) -> bool:
        return int(self) > int(other)

    def __int__(self) -> int:
        return int(str(self), 2)

    def __iter__(self) -> Iterator[int]:
        return iter(self._bits)

    def __len__(self) -> int:
        return len(self._bits)

    def __str__(self) -> str:
        return ''.join([str(bit) for bit in self._bits[::-1]])

    def __getitem__(self, item):
        return self._bits[item]

    def __contains__(self, bitsets: Bitsets) -> bool:
        return all(self[bit] == int(bool(bitsets[bit])) for bit in bitsets)

    has = __contains__

    def __or__(self, bitsets: Bitsets) -> 'Flags':
        new = Flags(self._bits)

        for bit, value in bitsets.items():
            new._bits[bit] = int(bool(value)) if value >= 0 else 1 - new._bits[bit]

        return new

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return cls(int.from_bytes(data, 'little'))

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(int(value), len(value) // 8, 'little')


__all__ = ["Enum", "Flags"]
