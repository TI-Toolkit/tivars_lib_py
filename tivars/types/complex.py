from typing import Type
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import *
from .real import *


class RealPart(Converter):
    _T = RealEntry

    @classmethod
    def get(cls, data: bytes, *, instance=None) -> _T:
        return instance.real_type.get(data)

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        value.subtype_id = instance.type_id[0]

        return instance.real_type.set(value, **kwargs)


class ImaginaryPart(Converter):
    _T = RealEntry

    @classmethod
    def get(cls, data: bytes, *, instance=None) -> _T:
        return instance.imag_type.get(data)

    @classmethod
    def set(cls, value: _T, *, instance=None, **kwargs) -> bytes:
        value.subtype_id = instance.type_id[0]

        return instance.imag_type.set(value, **kwargs)


class ComplexEntry(TIEntry):
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

    is_exact = False

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
        return RealEntry

    @property
    def imag_type(self) -> Type['RealEntry']:
        return RealEntry

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

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this complex number from a string representation

        :param string: The string to load
        """

        raise NotImplementedError

    def string(self) -> str:
        """
        :return: A string representation of this complex number
        """

        return f"{self.real} + {self.imag}i".replace("+ -", "- ")

    def coerce(self):
        self.raw.type_id = bytes([self.imag_subtype_id])

        super().coerce()


class TIComplex(ComplexEntry, register=True):
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

        self.real_subtype_id = self.imag_subtype_id = 0x0C

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains two real numbers, the real and imaginary parts
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

    @property
    def real_type(self) -> Type['TIReal']:
        return TIReal

    @property
    def imag_type(self) -> Type['TIReal']:
        return TIReal

    @Loader[complex, float, int]
    def load_complex(self, comp: complex):
        """
        Loads this complex number from a `complex`, upcasting as necessary

        :param comp: The complex number to load
        """

        real, imag = self.real_type(), self.imag_type()
        comp = complex(comp)

        real.load_float(comp.real)
        imag.load_float(comp.imag)

        self.real, self.imag = real, imag

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

        parts[1] = parts[1].replace("i", "") or "1"

        self.real = self.real_type(parts[0])
        self.imag = self.imag_type(parts[1])


class TIComplexFraction(TIComplex, register=True):
    is_exact = True

    _type_id = b'\x1B'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIComplexFraction` with specified meta and data values

        :param init: Data to initialize this complex number's data (defaults to `None`)
        :param for_flash: Whether this complex number supports flash chips (default to `True`)
        :param name: The name of this complex number (defaults to `A`)
        :param version: This complex number's version (defaults to `None`)
        :param archived: Whether this complex number is archived (defaults to `False`)
        :param data: This complex number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x1B

    @property
    def real_type(self) -> Type['TIRealFraction']:
        return TIRealFraction

    @property
    def imag_type(self) -> Type['TIRealFraction']:
        return TIRealFraction


class TIComplexRadical(ComplexEntry, register=True):
    flash_only = True

    min_data_length = 18

    is_exact = True

    _type_id = b'\x1D'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIComplexRadical` with specified meta and data values

        :param init: Data to initialize this complex number's data (defaults to `None`)
        :param for_flash: Whether this complex number supports flash chips (default to `True`)
        :param name: The name of this complex number (defaults to `A`)
        :param version: This complex number's version (defaults to `None`)
        :param archived: Whether this complex number is archived (defaults to `False`)
        :param data: This complex number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x1D

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains two real numbers, the real and imaginary parts
        """

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

    @property
    def real_type(self) -> Type['TIRealRadical']:
        return TIRealRadical

    @property
    def imag_type(self) -> Type['TIRealRadical']:
        return TIRealRadical

    def string(self) -> str:
        """
        :return: A string representation of this complex number
        """

        return f"{self.real} + {self.imag} * i"


class TIComplexPi(TIComplex, register=True):
    flash_only = True

    is_exact = True

    _type_id = b'\x1E'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIComplexPi` with specified meta and data values

        :param init: Data to initialize this complex number's data (defaults to `None`)
        :param for_flash: Whether this complex number supports flash chips (default to `True`)
        :param name: The name of this complex number (defaults to `A`)
        :param version: This complex number's version (defaults to `None`)
        :param archived: Whether this complex number is archived (defaults to `False`)
        :param data: This complex number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id, self.imag_subtype_id = 0x1B, 0x1E

    @property
    def real_type(self) -> Type['TIReal']:
        match self.real_subtype_id:
            case 0x1B:
                return TIRealFraction

            case 0x1C:
                return TIReal

            case _:
                warn(f"Real subtype ID 0x{self.real_subtype_id} not recognized for type {type(self)}.",
                     BytesWarning)

                return TIReal

    @property
    def imag_type(self) -> Type['TIRealPi']:
        return TIRealPi


class TIComplexPiFraction(TIComplexFraction, TIComplexPi, register=True):
    flash_only = True

    is_exact = True

    _type_id = b'\x1F'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "A",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        """
        Creates an empty `TIComplexPiFraction` with specified meta and data values

        :param init: Data to initialize this complex number's data (defaults to `None`)
        :param for_flash: Whether this complex number supports flash chips (default to `True`)
        :param name: The name of this complex number (defaults to `A`)
        :param version: This complex number's version (defaults to `None`)
        :param archived: Whether this complex number is archived (defaults to `False`)
        :param data: This complex number's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.real_subtype_id = self.imag_subtype_id = 0x1F

    @property
    def real_type(self) -> Type['TIReal']:
        match self.real_subtype_id:
            case 0x1E:
                return TIReal

            case 0x1F:
                return TIRealFraction

            case _:
                warn(f"Real subtype ID 0x{self.real_subtype_id} not recognized for type {type(self)}.",
                     BytesWarning)

                return TIReal

    @property
    def imag_type(self) -> Type['TIRealPi']:
        match self.imag_subtype_id:
            case 0x1E:
                return TIRealPi

            case 0x1F:
                return TIRealPiFraction

            case _:
                warn(f"Imag subtype ID 0x{self.imag_subtype_id} not recognized for type {type(self)}.",
                     BytesWarning)

                return TIRealPi

    def string(self) -> str:
        """
        :return: A string representation of this complex number
        """

        return f"{self.real} + {str(self.imag).replace(' /', 'i /')}"
