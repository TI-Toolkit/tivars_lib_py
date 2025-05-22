"""
Numeric helper functions and converters
"""


import decimal as dec

from .data import *


pi = dec.Decimal("3.1415926535898")
e = dec.Decimal("2.718281828459")


def sign(x: int) -> int:
    """
    Computes the mathematical sign of a number

    :param x: The input number
    :return: The sign of ``x``
    """

    return (x > 0) - (x < 0)


class BCD(Converter[int]):
    """
    Converter for 2-digit binary-coded decimal

    A single byte contains two decimal digits as if they were hex digits.
    """

    @classmethod
    def get(cls, data: bytes, **kwargs) -> int:
        """
        Converts ``bytes`` -> ``int`` from 2-digit binary coded decimal

        :param data: The raw bytes to convert
        :return: The number stored in ``data``
        """

        value = 0
        for byte in data:
            value *= 100
            tens, ones = divmod(byte, 16)
            value += 10 * tens + ones

        return value

    @classmethod
    def set(cls, value: int, *, length: int = None, **kwargs) -> bytes:
        """
        Converts ``int`` -> ``bytes`` as 2-digit binary coded decimal

        :param value: The value to convert
        :param length: The length of the data section
        :return: The bytes representing ``value`` in BCD
        """

        return int.to_bytes(int(str(value), 16), length if length is not None else 7, 'big')


class LeftNibbleBCD(Converter[int]):
    """
    Converter for 2-digit binary-coded decimal with a single extra nibble

    A single byte contains two decimal digits as if they were hex digits.
    The extraneous nibble appears in the leftmost byte, left-padded with a single hex digit.
    """

    @classmethod
    def get(cls, data: bytes, **kwargs) -> int:
        """
        Converts ``bytes`` -> ``int`` from 2-digit binary coded decimal with an extra nibble on the left

        :param data: The raw bytes to convert
        :return: The number stored in ``data``
        """

        value = data[0] % 16
        for byte in data[1:]:
            value *= 100
            tens, ones = divmod(byte, 16)
            value += 10 * tens + ones

        return value

    @classmethod
    def set(cls, value: int, *, current: bytes = None, **kwargs) -> bytes:
        """
        Converts ``int`` -> ``bytes`` as 2-digit binary coded decimal with an extra nibble on the left

        :param value: The value to convert
        :param current: The current value of the data section
        :return: The bytes representing ``value`` in BCD
        """

        data = bytearray(int.to_bytes(int(str(value), 16), 2, 'big'))
        data[0] += current[0] & 240

        return bytes(data)


class RightNibbleBCD(Converter[int]):
    """
    Converter for 2-digit binary-coded decimal with a single extra nibble

    A single byte contains two decimal digits as if they were hex digits.
    The extraneous nibble appears in the rightmost byte, right-padded with a single hex digit.
    """

    @classmethod
    def get(cls, data: bytes, **kwargs) -> int:
        """
        Converts ``bytes`` -> ``int`` from 2-digit binary coded decimal with an extra nibble on the right

        :param data: The raw bytes to convert
        :return: The number stored in ``data``
        """

        value = 0
        for byte in data[:-1]:
            value *= 100
            tens, ones = divmod(byte, 16)
            value += 10 * tens + ones

        return 10 * value + data[-1] // 16

    @classmethod
    def set(cls, value: int, *, current: bytes = None, **kwargs) -> bytes:
        """
        Converts ``int`` -> ``bytes`` as 2-digit binary coded decimal with an extra nibble on the right

        :param value: The value to convert
        :param current: The current value of the data section
        :return: The bytes representing ``value`` in BCD
        """

        data = bytearray(int.to_bytes(int(str(10 * value), 16), 2, 'big'))
        data[1] += current[1] % 16

        return bytes(data)


__all__ = ["pi", "e", "sign", "BCD", "LeftNibbleBCD", "RightNibbleBCD"]
