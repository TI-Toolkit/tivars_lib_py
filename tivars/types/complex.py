from typing import Type
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import *
from .real import *


class RealPart(Converter):
    """
    Converter for the real part of complex numbers

    Real parts are instances of `RealEntry`.
    """

    _T = RealEntry

    @classmethod
    def get(cls, data: bytes, *, instance=None) -> _T:
        """
        Converts `bytes` -> `RealType`

        :param data: The raw bytes to convert
        :param instance: The instance containing the data section
        :return: The real part of `data` converted to the appropriate type
        """

        return instance.real_type.get(data)

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        """
        Converts `RealEntry` -> `bytes`

        :param value: The value to convert
        :param instance: The instance containing the data section
        :return: The data of `value`
        """

        value.subtype_id = instance.get_real_subtype_id(type(value))

        return type(value).set(value, **kwargs)


class ImaginaryPart(Converter):
    """
    Converter for the imaginary part of complex numbers

    Imaginary parts are instances of `RealEntry`.
    """

    _T = RealEntry

    @classmethod
    def get(cls, data: bytes, *, instance=None) -> _T:
        """
        Converts `bytes` -> `RealType`

        :param data: The raw bytes to convert
        :param instance: The instance containing the data section
        :return: The real part of `data` converted to the appropriate type
        """

        return instance.imag_type.get(data)

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        """
        Converts `str` -> `bytes`

        :param value: The value to convert
        :param instance: The instance containing the data section
        :return: The data of `value`
        """

        value.subtype_id = instance.get_imag_subtype_id(type(value))

        return type(value).set(value, **kwargs)


class ComplexEntry(TIEntry):
    """
    Parser for complex numeric types

    This class handles floating-point types as well as the exact formats for the TI-83PCE and other newer models.
    The format for these types varies and is handled by `real_subtype_id` and `imag_subtype_id`.

    Two `RealEntry` types are used to form a single `ComplexEntry` corresponding to a complex number.
    These types need not be the same, and may have subtype IDs not corresponding to their native type IDs.
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

    is_exact = False
    """
    Whether this numeric type is exact
    """

    _real_subtypes = {None: RealEntry}

    _imag_subtypes = {None: RealEntry}

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    def __complex__(self):
        return self.complex()

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "":
                return self.string()
            case "t":
                return squash(replacer(self.string(), {"i": "[i]", " 1[i]": "[i]", "+ 0[i]": "", "0 +": "",
                                                       "-": "~"}))
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

    @View(data, RealPart)[0:9]
    def real(self) -> RealEntry:
        """
        The real part of the complex number
        """

    @View(data, ImaginaryPart)[9:18]
    def imag(self) -> RealEntry:
        """
        The imaginary part of the complex number
        """

    @View(data, Bits[0:6])[0:1]
    def real_subtype_id(self) -> bytes:
        """
        The subtype ID of the real part
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

        If this bit is set, the real part is negative.
        """

    @View(data, Bits[0:6])[9:10]
    def imag_subtype_id(self) -> bytes:
        """
        The subtype ID of the complex part
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

        If this bit is set, the complex part is negative.
        """

    @property
    def real_type(self) -> Type['RealEntry']:
        """
        :return: The subclass of `RealEntry` corresponding to this entry's `real_subtype_id`.
        """

        try:
            return self._real_subtypes[self.real_subtype_id]

        except KeyError:
            if self.real_subtype_id:
                warn(f"Real subtype ID 0x{self.real_subtype_id:x} not recognized for type {type(self)}.",
                     BytesWarning)

            return self._real_subtypes[self._type_id[0]]

    @property
    def imag_type(self) -> Type['RealEntry']:
        """
        :return: The subclass of `RealEntry` corresponding to this entry's `imag_subtype_id`.
        """

        try:
            return self._imag_subtypes[self.imag_subtype_id]

        except KeyError:
            if self.imag_subtype_id:
                warn(f"Imag subtype ID 0x{self.imag_subtype_id:x} not recognized for type {type(self)}.",
                     BytesWarning)

            return self._imag_subtypes[self._type_id[0]]

    @classmethod
    def get_real_subtype_id(cls, subtype: Type['RealEntry']) -> int:
        """
        Gets the subtype ID corresponding to the given subtype of the real part

        :param subtype: The subtype for the real part
        :return: The subtype ID used to identify `subtype` as a real part
        """

        return {v: k for k, v in cls._real_subtypes.items()}[subtype]

    @classmethod
    def get_imag_subtype_id(cls, subtype: Type['RealEntry']) -> int:
        """
        Gets the subtype ID corresponding to the given subtype of the imaginary part

        :param subtype: The subtype for the real part
        :return: The subtype ID used to identify `subtype` as an imaginary part
        """

        return {v: k for k, v in cls._imag_subtypes.items()}[subtype]

    def components(self) -> (RealEntry, RealEntry):
        """
        :return: The components of this complex number as a pair of `RealEntry` values
        """

        return self.real, self.imag

    @Loader[complex, float, int]
    def load_complex(self, comp: complex):
        """
        Loads this complex number from a `complex`, upcasting as necessary

        :param comp: The complex number to load
        """

        raise NotImplementedError

    def complex(self):
        """
        :return: The `complex` corresponding to this complex number
        """

        return self.real.float() + 1j * self.imag.float()

    def string(self) -> str:
        return f"{self.real} + {self.imag}i".replace("+ -", "- ")

    def coerce(self):
        self.raw.type_id = bytes([self.imag_subtype_id])

        super().coerce()


class TIComplex(ComplexEntry, register=True):
    """
    Parser for complex floating point values

    A `TIComplex` has 8 exponent bits and 14 decimal mantissa digits for each component.
    """

    min_data_length = 18

    _type_id = b'\x0C'

    _real_subtypes = {0x0C: TIReal}

    _imag_subtypes = {0x0C: TIReal}

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x0C

    @Section(min_data_length)
    def data(self) -> bytearray:
        pass

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

    @Loader[complex, float, int]
    def load_complex(self, comp: complex):
        real, imag = self.real_type(), self.imag_type()
        comp = complex(comp)

        real.load_float(comp.real)
        imag.load_float(comp.imag)

        self.real, self.imag = real, imag

    @Loader[str]
    def load_string(self, string: str):
        string = replacer(squash(string), {"-": "+-", "[i]": "i", "j": "i"})

        parts = string.split("+")
        if not parts[0]:
            parts = parts[1:]

        if len(parts) == 1:
            if "i" in parts[0]:
                parts = ["0", parts[0]]

            else:
                parts = [parts[0], "0i"]

        parts[1] = parts[1].replace("i", "") or "1"

        self.real = self.real_type(parts[0])
        self.imag = self.imag_type(parts[1])


class TIComplexFraction(TIComplex, register=True):
    """
    Parser for complex fractions

    A `TIComplexFraction` has 8 exponent bits and 14 decimal mantissa digits for each component.
    However, unlike a `TIComplex`, the floating point values are automatically converted to exact fractions on-calc.
    """

    is_exact = True

    _type_id = b'\x1B'

    _real_subtypes = {0x1B: TIRealFraction}

    _imag_subtypes = {0x1B: TIRealFraction}

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x1B


class TIComplexRadical(ComplexEntry, register=True):
    r"""
    Parser for complex radicals

    A `TIComplexRadical` is an exact sum of two square roots with rational scalars in both components.
    Specifically, a `TIComplexRadical` can represent numbers of the form

    $$\frac{\pm a\sqrt{b} \pm c\sqrt{d}}{e} + \frac{\pm m\sqrt{n} \pm o\sqrt{p}}{q} \times i$$

    where all values are non-negative integers. Additionally, $b > d \ge 0$, $n > p \ge 0$, $e > 0$, and $q > 0$.

    Each value is given three nibbles of storage in BCD format.
    Sign information for each radical is stored in an additional nibble.
    """

    flash_only = True

    min_data_length = 18

    is_exact = True

    _type_id = b'\x1D'

    _real_subtypes = {0x1D: TIRealRadical}

    _imag_subtypes = {0x1D: TIRealRadical}

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x1D

    @Section(min_data_length)
    def data(self) -> bytearray:
        pass

    @View(data, Bits[0:4])[1:2]
    def real_sign_type(self) -> int:
        """
        The sign type of the real part of the radical

        If the sign type is odd, the left scalar is negative.
        If the sign type is greater than one, the right scalar is negative.
        """

    @View(data, LeftNibbleBCD)[1:3]
    def real_denominator(self) -> int:
        """
        The denominator of the real part of the radical
        """

    @View(data, RightNibbleBCD)[3:5]
    def real_right_scalar(self) -> int:
        """
        The right scalar of the real part of the radical
        """

    @View(data, LeftNibbleBCD)[4:6]
    def real_left_scalar(self) -> int:
        """
        The left scalar of the real part of the radical
        """

    @View(data, RightNibbleBCD)[6:8]
    def real_right_radicand(self) -> int:
        """
        The right radicand of the real part of the radical
        """

    @View(data, LeftNibbleBCD)[7:9]
    def real_left_radicand(self) -> int:
        """
        The left radicand of the real part of the radical
        """

    @View(data, Bits[0:4])[10:11]
    def imag_sign_type(self) -> int:
        """
        The sign type of the imaginary part of the radical

        If the sign type is odd, the left scalar is negative.
        If the sign type is greater than one, the right scalar is negative.
        """

    @View(data, LeftNibbleBCD)[10:12]
    def imag_denominator(self) -> int:
        """
        The denominator of the imaginary part of the radical
        """

    @View(data, RightNibbleBCD)[12:14]
    def imag_right_scalar(self) -> int:
        """
        The right scalar of the imaginary part of the radical
        """

    @View(data, LeftNibbleBCD)[13:15]
    def imag_left_scalar(self) -> int:
        """
        The left scalar of the imaginary part of the radical
        """

    @View(data, RightNibbleBCD)[15:17]
    def imag_right_radicand(self) -> int:
        """
        The right radicand of the imaginary part of the radical
        """

    @View(data, LeftNibbleBCD)[16:18]
    def imag_left_radicand(self) -> int:
        """
        The left radicand of the imaginary part of the radical
        """

    @Loader[complex, float, int]
    def load_complex(self, comp: complex):
        return NotImplemented

    def string(self) -> str:
        return f"{self.real} + {self.imag} * i"


class TIComplexPi(TIComplex, register=True):
    """
    Parser for complex floating point values with imaginary integer multiples of π

    A `TIComplexPi` has real part equal to a `TIReal` or `TIRealFraction`.
    A `TIComplexPi` has imaginary part equal to an integral `TIReal` with an implicit factor of π.
    """

    flash_only = True

    is_exact = True

    _type_id = b'\x1E'

    _real_subtypes = {0x1B: TIRealFraction,
                      0x1C: TIReal}

    _imag_subtypes = {0x1E: TIRealPi}

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id, self.imag_subtype_id = 0x1B, 0x1E


class TIComplexPiFraction(TIComplexFraction, TIComplexPi, register=True):
    """
    Parser for complex fractional multiples of π

    A `TIComplexPiFraction` has real part equal to a `TIReal` or `TIRealFraction` with an implicit factor of π.
    A `TIComplexPiFraction` has imaginary part equal to a `TIReal` or `TIRealFraction` with an implicit factor of π.
    """

    flash_only = True

    is_exact = True

    _type_id = b'\x1F'

    _real_subtypes = {0x1E: TIReal,
                      0x1F: TIRealFraction}

    _imag_subtypes = {0x1E: TIRealPi,
                      0x1F: TIRealPiFraction}

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x1F

    def string(self) -> str:
        return f"{self.real} + {str(self.imag).replace(' /', 'i /')}"
