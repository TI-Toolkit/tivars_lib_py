import decimal as dec

from ..data import *


with dec.localcontext() as ctx:
    ctx.prec = 16
    pi, prev = 3, 0
    t = dec.Decimal(3)

    n, na, d, da = 1, 0, 0, 24
    while pi != prev:
        prev = pi

        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        pi += t

    ctx.prec = 14


def replacer(string: str, replacements: dict[str, str]) -> str:
    """
    Iteratively applies string replacements

    :param string: The input string
    :param replacements: The replacements to make
    :return: The input string with all replacements made in-order
    """

    for substring, replacement in replacements.items():
        string = string.replace(substring, replacement)

    return string


def sign(x: int) -> int:
    """
    Computes the mathematical sign of a number

    :param x: The input number
    :return: The sign of ``x``
    """

    return (x > 0) - (x < 0)


def squash(string: str) -> str:
    """
    Removes all spaces from a string

    :param string: The input string
    :return: The input string with all spaces removed
    """

    return ''.join(string.split())


class BCD(Converter):
    """
    Converter for 2-digit binary-coded decimal

    A single byte contains two decimal digits as if they were hex digits.
    """

    _T = int

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
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
    def set(cls, value: _T, **kwargs) -> bytes:
        """
        Converts ``int`` -> ``bytes`` as 2-digit binary coded decimal

        :param value: The value to convert
        :return: The bytes representing ``value`` in BCD
        """

        return int.to_bytes(int(str(value), 16), 7, 'big')


class LeftNibbleBCD(Converter):
    """
    Converter for 2-digit binary-coded decimal with a single extra nibble

    A single byte contains two decimal digits as if they were hex digits.
    The extraneous nibble appears in the leftmost byte, left-padded with a single hex digit.
    """

    _T = int

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
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
    def set(cls, value: _T, current: bytes = None, **kwargs) -> bytes:
        """
        Converts ``int`` -> ``bytes`` as 2-digit binary coded decimal with an extra nibble on the left

        :param value: The value to convert
        :param current: The current value of the data section
        :return: The bytes representing ``value`` in BCD
        """

        data = bytearray(int.to_bytes(int(str(value), 16), 2, 'big'))
        data[0] += current[0] & 240

        return bytes(data)


class RightNibbleBCD(Converter):
    """
    Converter for 2-digit binary-coded decimal with a single extra nibble

    A single byte contains two decimal digits as if they were hex digits.
    The extraneous nibble appears in the rightmost byte, right-padded with a single hex digit.
    """

    _T = int

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
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
    def set(cls, value: _T, current: bytes = None, **kwargs) -> bytes:
        """
        Converts ``int`` -> ``bytes`` as 2-digit binary coded decimal with an extra nibble on the right

        :param value: The value to convert
        :param current: The current value of the data section
        :return: The bytes representing ``value`` in BCD
        """

        data = bytearray(int.to_bytes(int(str(10 * value), 16), 2, 'big'))
        data[1] += current[1] % 16

        return bytes(data)


__all__ = ["pi", "replacer", "sign", "squash",
           "BCD", "LeftNibbleBCD", "RightNibbleBCD"]
