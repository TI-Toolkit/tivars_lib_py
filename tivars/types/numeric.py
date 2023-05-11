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
        value = 0
        for byte in data:
            value *= 100
            tens, ones = divmod(byte, 16)
            value += 10 * tens + ones

        return value

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(int(str(value), 16), 7, 'big')


def read_string(string: str) -> (int, int, bool):
    string = ''.join(string.split()).lower().replace("~", "-").replace("|e", "e")

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
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None,
                 flags: dict[int, int] = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        if flags is not None:
            self.flags |= flags

    def __int__(self) -> int:
        return self.int()

    def __float__(self) -> float:
        return self.float()

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
        The data section of the entry

        Contains flags, a mantissa, and an exponent
        """

    @View(data, FloatFlags)[0:1]
    def flags(self) -> FloatFlags:
        """
        Flags for the real number

        If bit 1 is set, the number is undefined
        If bits 2 and 3 are set and bit 1 is clear, the number if half of a complex number
        If bit 6 is set, something happened
        If bit 7 is set, the number is negative
        """

    @View(data, Integer)[1:2]
    def exponent(self) -> int:
        """
        The exponent of the real number

        The exponent has a bias of 0x80
        """

    @View(data, BCD)[2:9]
    def mantissa(self) -> int:
        """
        The mantissa of the real number

        The mantissa is 14 digits stored in BCD format, two digits per byte
        """

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        if isinstance(instance, TIComplex):
            instance.set_flags()

        return super(TIReal, cls).set(value, instance)

    @property
    def is_complex_component(self) -> bool:
        return FloatFlags.ComplexComponent in self.flags

    @property
    def is_undefined(self) -> bool:
        return FloatFlags.Undefined in self.flags

    @property
    def sign(self) -> int:
        return -1 if FloatFlags.Negative in self.flags else 1

    def load_decimal(self, decimal: dec.Decimal):
        self.load_string(str(decimal))

    def decimal(self) -> dec.Decimal:
        with dec.localcontext() as ctx:
            ctx.prec = 14
            decimal = dec.Decimal(self.sign * self.mantissa)
            decimal *= dec.Decimal(10) ** (self.exponent - 0x80 - 13)

        return decimal

    def load_float(self, decimal: float):
        self.load_decimal(dec.Decimal(decimal))

    def float(self) -> float:
        return float(self.decimal())

    def load_int(self, decimal: int):
        self.load_decimal(dec.Decimal(decimal))

    def int(self) -> int:
        return int(self.decimal())

    def load_string(self, string: str):
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
        string = f"{self.decimal():.14g}".rstrip("0").rstrip(".")

        if string.startswith("0e"):
            return "0"
        else:
            return string


class TIComplex(TIEntry):
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
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
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

        Bits 2 and 3 are set
        If bit 6 is set, something happened
        If bit 7 is set, the part is negative
        """

    @View(data, Integer)[1:2]
    def real_exponent(self) -> int:
        """
        The exponent of the real part of the complex number
        The exponent has a bias of 0x80
        """

    @View(data, BCD)[2:9]
    def real_mantissa(self) -> int:
        """
        The mantissa of the real part of the complex number
        The mantissa is 14 digits stored in BCD format, two digits per byte
        """

    @View(data, FloatFlags)[9:10]
    def imag_flags(self) -> FloatFlags:
        """
        Flags for the imaginary part of the complex number

        Bits 2 and 3 are set
        If bit 6 is set, something happened
        If bit 7 is set, the part is negative
        """

    @View(data, Integer)[10:11]
    def imag_exponent(self) -> int:
        """
        The exponent of the imaginary part of the complex number

        The exponent has a bias of 0x80
        """

    @View(data, BCD)[11:18]
    def imag_mantissa(self) -> int:
        """
        The mantissa of the imaginary part of the complex number

        The mantissa is 14 digits stored in BCD format, two digits per byte
        """

    def components(self) -> (TIReal, TIReal):
        return self.real, self.imag

    def set_flags(self):
        self.real_flags |= FloatFlags.ComplexComponent
        self.imag_flags |= FloatFlags.ComplexComponent

    def load_complex(self, comp: complex):
        real, imag = TIReal(), TIReal()

        real.load_float(comp.real)
        imag.load_float(comp.imag)

        self.real, self.imag = real, imag
        self.set_flags()

    def complex(self):
        return self.real.float() + 1j * self.imag.float()

    def load_string(self, string: str):
        string = ''.join(string.split()).replace("-", "+-").replace("[i]", "i")

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
        match str(self.real), str(self.imag):
            case "0", "0": return "0"
            case "0", _: return f"{self.imag}[i]"
            case _, "0": return f"{self.real}"
            case _, _: return f"{self.real} + {self.imag}[i]".replace("+ -", "- ")


__all__ = ["TIReal", "TIComplex", "BCD", "FloatFlags"]
