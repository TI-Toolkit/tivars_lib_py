import copy
import decimal as dec

from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry


class BCD(Converter):
    """
    Converter for 2-digit binary-coded decimal

    A single byte contains two decimal digits as if they were hex digits.
    """

    _T = int

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        """
        Converts `bytes` -> `int` from 2-digit binary coded decimal

        :param data: The raw bytes to convert
        :return: The 2-digit number stored in `data`
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
        Converts  `int` -> `bytes` as 2-digit binary coded decimal

        :param value: The value to convert
        :return: The bytes representing `value` in BCD
        """

        return int.to_bytes(int(str(value), 16), 7, 'big')


def replacer(string: str, replacements: dict[str, str]) -> str:
    for substring, replacement in replacements.items():
        string = string.replace(substring, replacement)

    return string


def squash(string: str) -> str:
    return ''.join(string.split())


def read_string(string: str) -> (int, int, bool):
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
        return 0, 0x80, neg

    exponent = int(exponent or "0")
    while not 0 < (value := int(integer)) < 10:
        if value == 0:
            integer, decimal = decimal[0], decimal[1:]
            exponent -= 1

        else:
            integer, decimal = integer[:-1], integer[-1] + decimal
            exponent += 1

    return int((integer + decimal).ljust(14, "0")[:14]), exponent + 0x80, neg


class Subtype:
    _subtype_id = None
    _subtype_ids = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        Subtype._subtype_ids[cls._subtype_id] = cls

    @classmethod
    def get_subtype(cls, subtype_id: int) -> 'Subtype':
        return cls._subtype_ids.get(subtype_id, None)


class TIReal(TIEntry, register=True):
    """
    Parser for real numeric types

    A standard `TIReal` is a signed floating point number with 8 exponent bits and 14 decimal mantissa digits.
    Two `TIReal` entries are used to form a single `TIComplex` complex number.

    The `TIReal` type also handles exact types found on the TI-83PCE and other newer models.
    The format for these types varies and is handled by a subtype value contained in the `flags` byte.
    """

    _T = 'TIReal'

    extensions = {
        None: "8xn",
        TI_82: "82n",
        TI_83: "83n",
        TI_82A: "8xn",
        TI_82P: "8xn",
        TI_83P: "8xn",
        TI_84P: "8xn",
        TI_84T: "8xn",
        TI_84PCSE: "8xn",
        TI_84PCE: "8xn",
        TI_84PCEPY: "8xn",
        TI_83PCE: "8xn",
        TI_83PCEEP: "8xn",
        TI_82AEP: "8xn"
    }

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

    def __float__(self) -> float:
        return self.float()

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "":
                return self.string()
            case "t":
                return self.string().replace("-", "~")
            case _:
                try:
                    return format(self.decimal(), format_spec)

                except (TypeError, ValueError):
                    return super().__format__(format_spec)

    def __int__(self) -> int:
        return int(self.float())

    def __neg__(self) -> 'TIReal':
        negated = copy.copy(self)
        negated.sign_bit = 1 - negated.sign_bit

        return negated

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the real number

        Contains flags, a mantissa, and an exponent.
        """

    @View(data, Bits[0:5])[0:1]
    def subtype(self) -> bytes:
        """
        The subtype of the number

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

        if not string:
            self.mantissa, self.exponent = 0, 0x80

        else:
            self.mantissa, self.exponent, self.sign_bit = read_string(string)

    def string(self) -> str:
        """
        :return: A string representation of this real
        """

        string = f"{self.decimal():.14g}".rstrip("0").rstrip(".")

        if string.startswith("0e"):
            return "0"
        else:
            return string


class TIComplex(TIEntry, register=True):
    """
    Parser for the complex numeric type

    A `TIComplex` is a pair of signed floating point numbers with 8 exponent bits and 14 decimal mantissa digits each.
    The pair corresponds to the real and imaginary parts of the number and share a common flag byte.
    """

    extensions = {
        None: "8xc",
        TI_82: "",
        TI_83: "83c",
        TI_82A: "8xc",
        TI_82P: "8xc",
        TI_83P: "8xc",
        TI_84P: "8xc",
        TI_84T: "8xc",
        TI_84PCSE: "8xc",
        TI_84PCE: "8xc",
        TI_84PCEPY: "8xc",
        TI_83PCE: "8xc",
        TI_83PCEEP: "8xc",
        TI_82AEP: "8xc"
    }

    min_data_length = 18

    _type_id = b'\x0C'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIComplex` with specified meta and data values

        :param init: Data to initialize this complex number's data (defaults to `None`)
        :param for_flash: Whether this complex number supports flash chips (default to `True`)
        :param name: The name of this complex number (defaults to `A`)
        :param version: This complex number's version (defaults to `None`)
        :param archived: Whether this complex number is archived (defaults to `False`)
        :param data: This complex number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    def __complex__(self):
        return self.complex()

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "":
                return self.string()
            case "t":
                return squash(replacer(self.string(), {"i": "[i]", "-": "~", "~ ": "- "}))
            case _:
                try:
                    return format(self.complex(), format_spec)

                except (TypeError, ValueError):
                    return super().__format__(format_spec)

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains two real numbers, the real and imaginary parts
        """

    @View(data, TIReal)[0:9]
    def real(self) -> TIReal:
        """
        The real part of the complex number
        """

    @View(data, TIReal)[9:18]
    def imag(self) -> TIReal:
        """
        The imaginary part of the complex number
        """

    @View(data, Bits[0:5])[0:1]
    def real_subtype(self) -> bytes:
        """
        The subtype of the real part

        The subtype of a complex component is always 0xC.
        """

    @View(data, Bits[6:7])[0:1]
    def real_graph_bit(self) -> int:
        """
        Whether the entry is used during graphing
        """

    @View(data, Bits[7:8])[0:1]
    def real_sign_bit(self) -> int:
        """
        The sign bit for the real part

        If this bit is set, the real part is negative
        """

    @View(data, Integer)[1:2]
    def real_exponent(self) -> int:
        """
        The exponent of the real part of the complex number

        The exponent has a bias of 0x80.
        """

    @View(data, BCD)[2:9]
    def real_mantissa(self) -> int:
        """
        The mantissa of the real part of the complex number

        The mantissa is 14 digits stored in BCD format, two digits per byte.
        """

    @View(data, Bits[0:5])[9:10]
    def imag_subtype(self) -> bytes:
        """
        The subtype of the complex part

        The subtype of a complex component is always 0xC.
        """

    @View(data, Bits[6:7])[9:10]
    def imag_graph_bit(self) -> int:
        """
        Whether the entry is used during graphing
        """

    @View(data, Bits[7:8])[9:10]
    def imag_sign_bit(self) -> int:
        """
        The sign bit for the complex part

        If this bit is set, the complex part is negative
        """

    @View(data, Integer)[10:11]
    def imag_exponent(self) -> int:
        """
        The exponent of the imaginary part of the complex number

        The exponent has a bias of 0x80.
        """

    @View(data, BCD)[11:18]
    def imag_mantissa(self) -> int:
        """
        The mantissa of the imaginary part of the complex number

        The mantissa is 14 digits stored in BCD format, two digits per byte.
        """

    def components(self) -> (TIReal, TIReal):
        """
        :return: The components of this complex number as a pair of `TIReal` values
        """

        return self.real, self.imag

    @Loader[complex, float, int]
    def load_complex(self, comp: complex):
        """
        Loads this complex number from a `complex`, upcasting as necessary

        :param comp: The complex number to load
        """

        real, imag = TIReal(), TIReal()
        comp = complex(comp)

        real.load_float(comp.real)
        imag.load_float(comp.imag)

        self.real, self.imag = real, imag
        self.real_subtype = self.imag_subtype = 0xC

    def complex(self):
        """
        :return: The `complex` corresponding to this complex number
        """
        return self.real.float() + 1j * self.imag.float()

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this complex number from a string representation

        :param string: The string to load
        """

        string = replacer(squash(string), {"-": "+-", "[i]": "i", "j": "i"})

        parts = string.split("+")
        if not parts[0]:
            parts = parts[1:]

        if len(parts) == 1:
            if "i" in parts[0]:
                parts = ["0", parts[0]]

            else:
                parts = [parts[0], "0i"]

        self.real = TIReal(parts[0])
        self.imag = TIReal(parts[1].replace("i", "") if parts[1] != "i" else "1")
        self.real_subtype = self.imag_subtype = 0xC

    def string(self) -> str:
        """
        :return: A string representation of this complex number
        """

        match str(self.real), str(self.imag):
            case "0", "0": return "0"
            case "0", _: return f"{self.imag}i".replace(" 1i", " i")
            case _, "0": return f"{self.real}"
            case _, _: return replacer(f"{self.real} + {self.imag}i", {"+ -": "- ", " 1i": " i"})


__all__ = ["TIReal", "TIComplex", "BCD"]
