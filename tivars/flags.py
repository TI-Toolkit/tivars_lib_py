"""
Flag and enum converters

This module implements two general-use converters:

    -   `Enum`, which provides conversion for a set of constants.

        Each element of an enum is assigned a literal that represents its value in a data section.

    -   `Flags`, which converts between a bitfield and a ``dict`` of bitsets.

        The ``dict`` representation permits the use of ``dict`` update notation to set flags with a single operation.
"""


from collections.abc import Mapping
from enum import IntEnum
from functools import total_ordering
from math import ceil

from .data import *


class Enum(Converter, IntEnum):
    """
    Base class for enum types

    This implementation subclasses Python's builtin `IntEnum` to interface with the `Converter` system.
    """

    @classmethod
    def get(cls, data: bytes, **kwargs) -> 'Enum':
        """
        Converts ``bytes`` -> ``Enum``, returning the first byte

        :param data: The raw bytes to convert
        :return: The first byte of ``data``
        """

        return cls(data[0])

    @classmethod
    def set(cls, value: 'Enum', **kwargs) -> bytes:
        """
        Converts ``Enum`` -> ``bytes``, enforcing that the input is a recognized enum value

        :param value: The value to convert
        :return: The byte in ``value``, unchanged
        """

        return bytes([value.value])


@total_ordering
class Flags(Converter, dict, Mapping[int, int]):
    """
    Base class for flag types

    Flags are bitfields in a byte that are set or cleared using dict update notation.
    """

    _T = 'Flags'

    def __init__(self, bitsets: Mapping[int, int] = None, *, width: int = 8):
        """
        Creates an empty `Flags` instance with a given initial state and width

        :param bitsets: The initial state of these flags
        :param width: The number of bitfields used for these flags (defaults to ``8``)
        """

        if bitsets is None:
            bitsets = {bit: 0 for bit in range(width)}

        else:
            bitsets = {bit: 0 for bit in range(ceil((max(bitsets.keys(), default=0) + 1) / 8) * 8)} | bitsets

        super().__init__({bit: value % 2 for bit, value in bitsets.items()})

    def __gt__(self, other) -> bool:
        return int(self) > int(other)

    def __int__(self) -> int:
        return int(str(self), 2)

    def __str__(self) -> str:
        return ''.join([str(bit) for bit in self.values()][::-1])

    def __contains__(self, bitsets: Mapping[int, int]) -> bool:
        return all(self[bit] == int(bool(bitsets[bit])) for bit in bitsets)

    has = __contains__

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        """
        Converts ``bytes`` -> `Flags`, splitting the byte into the corresponding bitfields

        :param data: The raw bytes to convert
        :return: A `Flags` instance with bitfields given by ``data``
        """

        return cls({bit: int(value) for bit, value in enumerate(f"{int.from_bytes(data, 'little'):b}"[::-1])})

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        """
        Converts `Flags` -> ``bytes``, packing the bitfields into the appropriate number of bytes

        :param value: The value to convert
        :return: The byte string composed of the bitfields given in ``value``
        """

        return int.to_bytes(int(value), len(value) // 8, 'little')


__all__ = ["Enum", "Flags"]
