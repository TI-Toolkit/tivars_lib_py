import copy
import decimal as dec
import fractions as frac
import re

from typing import Type

from tivars.models import *
from .numeric import *
from ..data import *
from ..var import TIEntry


class RealEntry(TIEntry):
    """
    Parser for real numeric types

    This class handles floating-point types as well as the exact formats for the TI-83PCE and other newer models.
    The format for these types varies and is handled by the `subtype_id`, the first six bits of the first data byte.

    Two `RealEntry` types are used to form a single `ComplexEntry` corresponding to a complex number.
    """

    _T = 'RealEntry'

    extensions = {
        None: "8xn",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xn",
        TI_83PCE: "8xn",
        TI_83PCEEP: "8xn",
        TI_82AEP: "8xn"
    }

    min_data_length = 9

    min_exponent = 0x00
    """
    The smallest allowed floating point exponent
    """

    is_exact = False
    """
    Whether this numeric type is exact
    """

    def __float__(self) -> float:
        return self.float()

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "":
                return self.string()
            case "j":
                return str(self.json_number())
            case "t":
                return squash(re.sub(r"(√\d*)", r"sqrt(\1)", replacer(self.string(), {"-": "~", "/": "n/d"})))
            case _:
                try:
                    return format(self.decimal(), format_spec)

                except (TypeError, ValueError):
                    return super().__format__(format_spec)

    def __int__(self) -> int:
        return int(self.float())

    def __neg__(self) -> 'RealEntry':
        negated = copy.copy(self)
        negated.sign_bit = 1 - negated.sign_bit

        return negated

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the real number
        """

    @View(data, Bits[0:6])[0:1]
    def subtype_id(self) -> bytes:
        """
        The subtype ID of the number

        Differentiates the exact radical and fraction formats.
        """

    @View(data, Bits[6:7])[0:1]
    def graph_bit(self) -> int:
        """
        Whether the entry is used during graphing
        """

    @View(data, Bits[7:8])[0:1]
    def sign_bit(self) -> int:
        """
        The sign bit for the number

        If this bit is used, the number is negative when set.
        """

    @property
    def subtype(self) -> Type['RealEntry']:
        """
        :return: The subtype of this real number
        """

        return self.get_type(self.subtype_id)

    @property
    def sign(self) -> int:
        """
        :return: The sign of this real number
        """

        return -1 if self.sign_bit else 1

    @Loader[dec.Decimal]
    def load_decimal(self, decimal: dec.Decimal):
        """
        Loads a `dec.Decimal` into this real number

        :param decimal: The decimal to load
        """

        raise NotImplementedError

    def decimal(self) -> dec.Decimal:
        """
        :return: A `dec.Decimal` object corresponding to this real number
        """

        raise NotImplementedError

    @Loader[float, int]
    def load_float(self, decimal: float):
        """
        Loads a `float` into this real number, upcasting as necessary

        :param decimal: The float to load
        """

        self.load_decimal(dec.Decimal(decimal))

    def json_number(self) -> float | str:
        """
        Encoder for JSON implementations with potentially low precision

        :return: A `float` or `str` depending on whether this real number can be contained in a single-precision float
        """

        if len(str(number := self.float())) <= 6:
            return number

        else:
            return str(number)

    def float(self) -> float:
        """
        :return: The `float` corresponding to this real number
        """

        return float(self.decimal())

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this real number from a string representation

        :param string: The string to load
        """

        raise NotImplementedError

    def string(self) -> str:
        """
        :return: A string representation of this real number
        """

        raise NotImplementedError

    def coerce(self):
        self.raw.type_id = bytes([self.subtype_id])

        super().coerce()


class TIReal(RealEntry, register=True):
    """
    Parser for real floating point values

    A `TIReal` has 8 exponent bits and 14 decimal mantissa digits.

    A `TIReal` entry can be used to form `TIComplex` or `TIComplexPi` complex numbers.
    """

    min_data_length = 9

    _type_id = b'\x00'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIReal` with specified meta and data values

        :param init: Data to initialize this real number's data (defaults to `None`)
        :param for_flash: Whether this real number supports flash chips (default to `True`)
        :param name: The name of this real number (defaults to `A`)
        :param version: This real number's version (defaults to `None`)
        :param archived: Whether this real number is archived (defaults to `False`)
        :param data: This real number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the real number

        Contains flags, a mantissa, and an exponent.
        """

    @View(data, Integer)[1:2]
    def exponent(self) -> int:
        """
        The exponent of the real number

        The exponent has a bias of 0x80.
        """

    @View(data, BCD)[2:9]
    def mantissa(self) -> int:
        """
        The mantissa of the real number

        The mantissa is 14 digits stored in BCD format, two digits per byte.
        """

    @Loader[dec.Decimal]
    def load_decimal(self, decimal: dec.Decimal):
        """
        Loads a `dec.Decimal` into this real number

        :param decimal: The decimal to load
        """

        self.load_string(str(decimal))

    def decimal(self) -> dec.Decimal:
        """
        :return: A `dec.Decimal` object corresponding to this real number
        """

        with dec.localcontext() as ctx:
            ctx.prec = 14
            decimal = dec.Decimal(self.sign * self.mantissa)
            decimal *= dec.Decimal(10) ** (self.exponent - 0x80 - 13)

        return decimal

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this real number from a string representation

        :param string: The string to load
        """

        if not string:
            self.mantissa, self.exponent, self.sign_bit = 0, 0x80, False
            return

        string = replacer(squash(string).lower(), {"~": "-", "|e": "e"})

        if "e" not in string:
            string += "e0"

        if "." not in string:
            string = string.replace("e", ".e")

        neg = string.startswith("-")
        string = string.strip("+-")

        number, exponent = string.split("e")
        integer, decimal = number.split(".")
        integer, decimal = integer or "0", decimal or "0"

        if int(integer) == int(decimal) == 0:
            self.mantissa, self.exponent, self.sign_bit = 0, 0x80, neg
            return

        exponent = int(exponent or "0")
        while not 0 < (value := int(integer)) < 10:
            if value == 0:
                integer, decimal = decimal[0], decimal[1:]
                exponent -= 1

            else:
                integer, decimal = integer[:-1], integer[-1] + decimal
                exponent += 1

        self.mantissa, self.exponent, self.sign_bit = int((integer + decimal).ljust(14, "0")[:14]), exponent + 0x80, neg

    def string(self) -> str:
        """
        :return: A string representation of this real number
        """

        string = f"{self.decimal():.14g}".rstrip("0").rstrip(".")

        if string.startswith("0e"):
            return "0"
        else:
            return string


class TIRealFraction(TIReal, register=True):
    """
    Parser for real fractions

    A `TIRealFraction` has 8 exponent bits and 14 decimal mantissa digits.
    However, unlike a `TIReal`, the floating point value is automatically converted to an exact fraction on-calc.

    A `TIRealFraction` can be used to form `TIComplexFraction`, `TIComplexPi`, or `TIComplexPiFraction` complex numbers.
    """

    min_exponent = 0x7C

    is_exact = True

    _type_id = b'\x18'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIRealFraction` with specified meta and data values

        :param init: Data to initialize this real number's data (defaults to `None`)
        :param for_flash: Whether this real number supports flash chips (default to `True`)
        :param name: The name of this real number (defaults to `A`)
        :param version: This real number's version (defaults to `None`)
        :param archived: Whether this real number is archived (defaults to `False`)
        :param data: This real number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.subtype_id = 0x18

    @Loader[frac.Fraction]
    def load_fraction(self, fraction: frac.Fraction):
        """
        Loads a `frac.Fraction` into this real number

        :param fraction: The fraction to load
        """

        with dec.localcontext() as ctx:
            ctx.prec = 14
            decimal = dec.Decimal(fraction.numerator) / fraction.denominator

        super().load_string(str(decimal))

    def fraction(self) -> frac.Fraction:
        """
        :return: A `frac.Fraction` object corresponding to this real number
        """

        return frac.Fraction(self.decimal())

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this real number from a string representation

        :param string: The string to load
        """

        self.load_fraction(frac.Fraction(string))

    def string(self) -> str:
        """
        :return: A string representation of this real number
        """

        return "%d / %d" % self.fraction().as_integer_ratio()


class TIRealRadical(RealEntry, register=True):
    r"""
    Parser for real radicals

    A `TIRealRadical` is an exact sum of two square roots with rational scalars.
    Specifically, a `TIRealRadical` can represent numbers of the form

    $$\frac{\pm a\sqrt{b} \pm c\sqrt{d}}{e}$$

    where all values are non-negative integers. Additionally, $b > d \ge 0$ and $e > 0$.

    Each value is given three nibbles of storage in BCD format.
    Sign information for each radical is stored in an additional nibble.

    A `TIRealRadical` can be used to form `TIComplexRadical` complex numbers.
    """

    flash_only = True

    min_data_length = 9

    is_exact = True

    _type_id = b'\x1C'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIRealRadical` with specified meta and data values

        :param init: Data to initialize this real radical's data (defaults to `None`)
        :param for_flash: Whether this real radical supports flash chips (default to `True`)
        :param name: The name of this real radical (defaults to `A`)
        :param version: This real radical's version (defaults to `None`)
        :param archived: Whether this real radical is archived (defaults to `False`)
        :param data: This real radical's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.subtype_id = 0x1C

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the real radical

        Contains the scalars, radicands, denominator, and sign type.
        """

    @View(data, Bits[0:4])[1:2]
    def sign_type(self) -> int:
        """
        The sign type of the real radical

        If the sign type is odd, the left scalar is negative.
        If the sign type is greater than one, the right scalar is negative.
        """

    @View(data, LeftNibbleBCD)[1:3]
    def denominator(self) -> int:
        """
        The denominator of the real radical
        """

    @View(data, RightNibbleBCD)[3:5]
    def right_scalar(self) -> int:
        """
        The right scalar of the real radical
        """

    @View(data, LeftNibbleBCD)[4:6]
    def left_scalar(self) -> int:
        """
        The left scalar of the real radical
        """

    @View(data, RightNibbleBCD)[6:8]
    def right_radicand(self) -> int:
        """
        The right radicand of the real radical
        """

    @View(data, LeftNibbleBCD)[7:9]
    def left_radicand(self) -> int:
        """
        The left radicand of the real radical
        """

    @property
    def sign(self) -> int:
        """
        :return: The sign of this real number
        """

        return -1 if self.decimal() < 0 else 1

    @Loader[dec.Decimal]
    def load_decimal(self, decimal: dec.Decimal):
        """
        Loads a `dec.Decimal` into this real number

        :param decimal: The decimal to load
        """

        return NotImplemented

    def decimal(self) -> dec.Decimal:
        """
        :return: A `dec.Decimal` object corresponding to this real number
        """

        return (self.left_scalar * (-1 if self.sign_type % 2 else 1) * dec.Decimal(self.left_radicand).sqrt() +
                self.right_scalar * (-1 if self.sign_type > 1 else 1) * dec.Decimal(self.right_radicand).sqrt()) \
            / self.denominator

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this real number from a string representation

        :param string: The string to load
        """

        if not string:
            self.sign_type, self.denominator = 0, 1
            self.left_scalar, self.left_radicand = 0, 0
            self.right_scalar, self.right_radicand = 0, 0

        string = replacer(squash(string), {"(": "", ")": "", "*": "", "~": "-", "sqrt": "√", "-": "+-"}).lstrip("+")

        if "." in string:
            raise ValueError("radical type only accepts integer components")

        if "/" not in string:
            string += "/1"

        if "√" not in string:
            string = "0√0+" + string
            string = string.replace("/", "√1/")

        if "+" not in string:
            string = string.replace("/", "+0√0/")

        top, bot = string.split("/")
        left, right = top.split("+")

        if "√" not in left:
            left += "√1"

        if "√" not in right:
            right += "√1"

        left_scalar, left_radicand = left.split("√")
        right_scalar, right_radicand = right.split("√")

        left_scalar = int(left_scalar if left_scalar.rstrip("+-") else left_scalar + "1")
        left_radicand = int(left_radicand)
        right_scalar = int(right_scalar if right_scalar.rstrip("+-") else right_scalar + "1")
        right_radicand = int(right_radicand)

        if left_radicand < 0 or right_radicand < 0:
            raise ValueError("square roots cannot be negative")

        if left_radicand < right_radicand:
            left_scalar, right_scalar = right_scalar, left_scalar
            left_radicand, right_radicand = right_radicand, left_radicand

        elif left_radicand == right_radicand:
            left_scalar += right_scalar
            right_scalar = right_radicand = 0

        denominator = int(bot.lstrip("+"))

        if denominator == 0:
            raise ValueError("denominator must be nonzero")

        left_scalar, right_scalar = left_scalar * sign(denominator), right_scalar * sign(denominator)
        match sign(left_scalar), sign(right_scalar):
            case 1, -1:
                self.sign_type = 2
            case 1, _:
                self.sign_type = 0
            case -1, 1:
                self.sign_type = 1
            case -1, _:
                self.sign_type = 3

            case _:
                raise ValueError(f"invalid sign type {(sign(left_scalar), sign(right_scalar))}")

        self.denominator = abs(denominator)
        self.left_scalar, self.right_scalar = abs(left_scalar), abs(right_scalar)
        self.left_radicand, self.right_radicand = left_radicand, right_radicand

    def string(self) -> str:
        """
        :return: A string representation of this real number
        """

        left = f"{self.left_scalar * (-1 if self.sign_type % 2 else 1)}√{self.left_radicand}"
        right = f"{self.right_scalar * (-1 if self.sign_type > 1 else 1)}√{self.right_radicand}"

        return f"({left} + {right}) / {self.denominator}".replace("+ -", "- ")


class TIRealPi(TIReal, register=True):
    """
    Parser for real floating point multiples of π

    A `TIRealPi` is simply a `TIReal` with an implicit factor of π.

    A `TIRealPi` can be used to form `TIComplexPi` or `TIComplexPiFraction` complex numbers.
    """

    flash_only = True

    min_exponent = 0x7C

    is_exact = True

    _type_id = b'\x20'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIRealPi` with specified meta and data values

        :param init: Data to initialize this real number's data (defaults to `None`)
        :param for_flash: Whether this real number supports flash chips (default to `True`)
        :param name: The name of this real number (defaults to `A`)
        :param version: This real number's version (defaults to `None`)
        :param archived: Whether this real number is archived (defaults to `False`)
        :param data: This real number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.subtype_id = 0x20

    def string(self) -> str:
        """
        :return: A string representation of this real number
        """

        return super().string() + "π"


class TIRealPiFraction(TIRealFraction, TIRealPi, register=True):
    """
    Parser for real fractional multiples of π

    A `TIRealPiFraction` is simply a `TIRealFraction` with an implicit factor of π.

    A `TIRealPiFraction` can be used to form `TIComplexPiFraction` complex numbers.
    """

    flash_only = True

    _type_id = b'\x21'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIRealPiFraction` with specified meta and data values

        :param init: Data to initialize this real number's data (defaults to `None`)
        :param for_flash: Whether this real number supports flash chips (default to `True`)
        :param name: The name of this real number (defaults to `A`)
        :param version: This real number's version (defaults to `None`)
        :param archived: Whether this real number is archived (defaults to `False`)
        :param data: This real number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.subtype_id = 0x21

    def string(self) -> str:
        """
        :return: A string representation of this real number
        """

        return super().string().replace(" /", "π /")


__all__ = ["TIReal", "TIRealFraction", "TIRealRadical", "TIRealPi", "TIRealPiFraction", "RealEntry"]
