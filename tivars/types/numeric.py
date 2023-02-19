import decimal as dec
import warnings

from tivars.models import *
from ..data import *
from ..var import TIEntry


def to_bcd(number: int) -> bytes:
    return int.to_bytes(int(str(number), 16), 7, 'big')


def from_bcd(bcd: bytes) -> int:
    number = 0
    for byte in bcd:
        number *= 100
        tens, ones = divmod(byte, 16)
        number += 10 * tens + ones

    return number


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

    exponent = int(exponent or "0")
    while len(integer) > 1:
        decimal = integer[-1] + decimal
        integer = integer[:-1]
        exponent += 1

    return int((integer + decimal).ljust(14, "0")[:14]), exponent + 0x80, neg


Mantissa = (to_bcd, from_bcd)


class TIReal(TIEntry):
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

    _type_id = b'\x00'

    @Section(9)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains flags, a mantissa, and an exponent
        """

    @View(data, Integer)[0:1]
    def flags(self) -> int:
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

    @View(data, Mantissa)[2:9]
    def mantissa(self) -> int:
        """
        The mantissa of the real number

        The mantissa is 14 digits stored in BCD format, two digits per byte
        """

    @property
    def is_complex_component(self) -> bool:
        return self.flags & 1 << 2 & 1 << 3 & ~1 << 1

    @property
    def is_undefined(self) -> bool:
        return self.flags & 1 << 1

    @property
    def sign(self) -> int:
        return -1 if self.flags & 1 << 7 else 1

    # Out of order because type annotations suck
    def load_decimal(self, decimal: dec.Decimal):
        self.load_string(str(decimal))

    def decimal(self) -> dec.Decimal:
        with dec.localcontext() as ctx:
            ctx.prec = 14
            decimal = dec.Decimal(self.sign * self.mantissa)
            decimal *= dec.Decimal(10) ** (self.exponent - 0x80 - 13)

        return decimal

    def load_string(self, string: str):
        self.mantissa, self.exponent, neg = read_string(string)

        if neg:
            self.negate()

    def make_complex_component(self):
        self.flags |= 1 << 3 | 1 << 2
        self.flags &= ~1 << 1

    def negate(self):
        self.flags ^= 1 << 7

    def string(self) -> str:
        return f"{self.decimal().quantize(dec.Decimal(10) ** -10):.10g}".rstrip("0").rstrip(".").replace("0e-1", "0")


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

    _type_id = b'\x0C'

    @Section(18)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains two real numbers, the real and imaginary parts
        """

    @View(data, Integer)[0:1]
    def real_flags(self) -> int:
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

    @View(data, Mantissa)[2:9]
    def real_mantissa(self) -> int:
        """
        The mantissa of the real part of the complex number

        The mantissa is 14 digits stored in BCD format, two digits per byte
        """

    @View(data, Integer)[9:10]
    def imag_flags(self) -> int:
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

    @View(data, Mantissa)[11:18]
    def imag_mantissa(self) -> int:
        """
        The mantissa of the imaginary part of the complex number

        The mantissa is 14 digits stored in BCD format, two digits per byte
        """

    def components(self) -> (TIReal, TIReal):
        return self.real, self.imag

    @property
    def imag(self) -> TIReal:
        imag = TIReal()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            imag.load_bytes(self.bytes()[:-18] + self.bytes()[-9:])

        return imag

    @property
    def real(self) -> TIReal:
        real = TIReal()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            real.load_bytes(self.bytes()[:-9])

        return real

    def load_components(self, *, components: (TIReal, TIReal) = (None, None), real: TIReal = None, imag: TIReal = None):
        real = real or components[0]
        imag = imag or components[1]

        if real is not None:
            self.real_flags, self.real_exponent, self.real_mantissa = real.flags, real.exponent, real.mantissa

        if imag is not None:
            self.imag_flags, self.imag_exponent, self.imag_mantissa = imag.flags, imag.exponent, imag.mantissa

        self.set_flags()

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

        self.real_mantissa, self.real_exponent, real_neg = read_string(parts[0])
        self.imag_mantissa, self.imag_exponent, imag_neg = read_string(parts[1].replace("i", "")
                                                                       if parts[1] != "i" else "1")

        if real_neg:
            self.real_flags ^= 1 << 7

        if imag_neg:
            self.imag_flags ^= 1 << 7

        self.set_flags()

    def set_flags(self):
        self.real_flags |= 1 << 3 | 1 << 2
        self.real_flags &= ~1 << 1

        self.imag_flags |= 1 << 3 | 1 << 2
        self.imag_flags &= ~1 << 1

    def string(self) -> str:
        return f"{self.real} + {self.imag}[i]".replace("+ -", "- ").replace("0 + ", "").replace(" + 0[i]", "")


class ListVar(TIEntry):
    item_type = TIEntry

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the length of the list, followed by sequential variable data sections
        """

    @View(data, Integer)[0:2]
    def length(self) -> int:
        """
        The length of the list
        """

    # ALSO out of order because type annotations suck
    def load_list(self, lst: list[item_type]):
        self.clear()
        self.data += int.to_bytes(len(lst), 2, 'little')

        for entry in lst:
            self.data += entry.data

    def list(self) -> list[item_type]:
        lst = []
        for i in range(self.length):
            entry = self.item_type()

            entry.meta_length = self.meta_length
            entry.name = self.name
            entry.version = self.version
            entry.archived = self.archived

            entry.data = self.data[entry.data_length * i + 2:][:entry.data_length]
            lst.append(entry)

        return lst

    def load_string(self, string: str):
        lst = []

        for string in ''.join(string.strip("[]").split()).split(","):
            entry = self.item_type()
            entry.load_string(string)
            lst.append(entry)

        self.load_list(lst)

    def string(self) -> str:
        return f"[{', '.join(str(entry) for entry in self.list())}]"


class TIRealList(ListVar):
    item_type = TIReal

    extensions = {
        None: "8xl",
        TI_82: "82l",
        TI_83: "83l",
        TI_82A: "8xl",
        TI_82P: "8xl",
        TI_83P: "8xl",
        TI_84P: "8xl",
        TI_84T: "8xl",
        TI_84PCSE: "8xl",
        TI_84PCE: "8xl",
        TI_84PCEPY: "8xl",
        TI_83PCE: "8xl",
        TI_83PCEEP: "8xl",
        TI_82AEP: "8xl"
    }

    _type_id = b'\x01'


class TIComplexList(ListVar):
    item_type = TIComplex

    extensions = {
        None: "8xl",
        TI_82: "",
        TI_83: "83l",
        TI_82A: "8xl",
        TI_82P: "8xl",
        TI_83P: "8xl",
        TI_84P: "8xl",
        TI_84T: "8xl",
        TI_84PCSE: "8xl",
        TI_84PCE: "8xl",
        TI_84PCEPY: "8xl",
        TI_83PCE: "8xl",
        TI_83PCEEP: "8xl",
        TI_82AEP: "8xl"
    }

    _type_id = b'\x0D'


__all__ = ["TIReal", "TIComplex", "TIRealList", "TIComplexList"]