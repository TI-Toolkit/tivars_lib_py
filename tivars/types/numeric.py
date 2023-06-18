import copy
import decimal as dec

from warnings import warn

from tivars.models import *
from ..data import *
from ..flags import *
from ..var import TIEntry


class BCD(Converter):
    _T = int

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        """
        Converts `bytes` -> `int` from 2-digit binary coded decimal

        :param data: The raw bytes to convert
        :param instance: The instance which contains the data section (usually unused)
        :return: The 2-digit number stored in `data`
        """

        value = 0
        for byte in data:
            value *= 100
            tens, ones = divmod(byte, 16)
            value += 10 * tens + ones

        return value

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        """
        Converts  `int` -> `bytes` as 2-digit binary coded decimal

        :param value: The value to convert
        :param instance: The instance which contains the data section (usually unused)
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


class FloatFlags(Flags):
    Undefined = {1: 1}
    Defined = {1: 0}
    ComplexComponent = {1: 0, 2: 1, 3: 1}
    Modified = {6: 1}
    Positive = {7: 0}
    Negative = {7: 1}


class TIReal(TIEntry):
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
                 data: bytearray = None,
                 flags: dict[int, int] = None):
        """
        Creates an empty `TIReal` with specified meta and data values

        :param init: Data to initialize this real number's data (defaults to `None`)
        :param for_flash: Whether this real number supports flag chips (default to `True`)
        :param name: The name of this real number (defaults to `'A'`)
        :param version: This real number's version (defaults to `None`)
        :param archived: Whether this real number is archived (defaults to `False`)
        :param data: This real number's data (defaults to empty)
        :param flags: This real number's flags (defaults to no bits set)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        if flags is not None:
            self.flags |= flags

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
        return self.int()

    def __neg__(self) -> 'TIReal':
        negated = copy.copy(self)
        if FloatFlags.Positive in self.flags:
            negated.flags |= FloatFlags.Negative

        else:
            negated.flags |= FloatFlags.Negative

        return negated

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the real number

        Contains flags, a mantissa, and an exponent.
        """

    @View(data, FloatFlags)[0:1]
    def flags(self) -> FloatFlags:
        """
        Flags for the real number
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

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        if isinstance(instance, TIComplex):
            instance.set_flags()

        return super(TIReal, cls).set(value, instance)

    @property
    def is_complex_component(self) -> bool:
        """
        :return: Whether this real number is part of a complex number
        """

        return FloatFlags.ComplexComponent in self.flags

    @property
    def is_undefined(self) -> bool:
        """
        :return: Whether this real number is undefined
        """

        return FloatFlags.Undefined in self.flags

    @property
    def sign(self) -> int:
        """
        :return: The sign of this real number
        """

        return -1 if FloatFlags.Negative in self.flags else 1

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
            self.flags |= FloatFlags.Undefined

        else:
            self.mantissa, self.exponent, neg = read_string(string)

            if neg:
                self.flags |= FloatFlags.Negative

            else:
                self.flags |= FloatFlags.Positive

    def string(self) -> str:
        """
        :return: A string representation of this real
        """

        string = f"{self.decimal():.14g}".rstrip("0").rstrip(".")

        if string.startswith("0e"):
            return "0"
        else:
            return string


class TIComplex(TIEntry):
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
        :param for_flash: Whether this complex number supports flag chips (default to `True`)
        :param name: The name of this complex number (defaults to `'A'`)
        :param version: This complex number's version (defaults to `None`)
        :param archived: Whether this complex number is archived (defaults to `False`)
        :param data: This complex number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        if data:
            if FloatFlags.ComplexComponent not in self.real_flags:
                warn("Bits 2 and 3 of the real component flags should be set in a complex entry.",
                     BytesWarning)

            if FloatFlags.ComplexComponent not in self.imag_flags:
                warn("Bits 2 and 3 of the imaginary component flags should be set in a complex entry.",
                     BytesWarning)

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

    @View(data, FloatFlags)[0:1]
    def real_flags(self) -> FloatFlags:
        """
        Flags for the real part of the complex number
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

    @View(data, FloatFlags)[9:10]
    def imag_flags(self) -> FloatFlags:
        """
        Flags for the imaginary part of the complex number
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

    def set_flags(self):
        self.real_flags |= FloatFlags.ComplexComponent
        self.imag_flags |= FloatFlags.ComplexComponent

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
        self.set_flags()

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
        self.set_flags()

    def string(self) -> str:
        """
        :return: A string representation of this complex number
        """

        match str(self.real), str(self.imag):
            case "0", "0": return "0"
            case "0", _: return f"{self.imag}i".replace(" 1i", " i")
            case _, "0": return f"{self.real}"
            case _, _: return replacer(f"{self.real} + {self.imag}i", {"+ -": "- ", " 1i": " i"})


__all__ = ["TIReal", "TIComplex", "BCD", "FloatFlags"]
