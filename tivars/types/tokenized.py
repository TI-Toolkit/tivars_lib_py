import re

from io import BytesIO
from typing import ByteString
from warnings import warn

from tivars.models import *
from tivars.tokenizer import *
from ..data import *
from ..var import SizedEntry


class TokenizedEntry(SizedEntry):
    """
    Base class for all tokenized entries

    A tokenized entry is a `SizedEntry` whose data comprises a stream of tokens.
    """

    versions = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
        0x0A, 0x0B, 0x0C,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26,
        0x2A, 0x2B, 0x2C
    ]

    min_data_length = 2

    clock_tokens = [
        b'\xEF\x00', b'\xEF\x01', b'\xEF\x02', b'\xEF\x03', b'\xEF\x04',
        b'\xEF\x07', b'\xEF\x08', b'\xEF\x09', b'\xEF\x0A', b'\xEF\x0B', b'\xEF\x0C', b'\xEF\x0D',
        b'\xEF\x0E', b'\xEF\x0F', b'\xEF\x10'
    ]
    """
    Tokens which interface with the RTC
    
    These tokens influence the entry's version, though detecting the presence of the RTC has no current application.
    """

    def __format__(self, format_spec: str) -> str:
        if "." not in format_spec:
            format_spec += ".en"

        spec, lang = format_spec.split(".")

        match spec:
            case "":
                return self.decode(self.data, lang=lang)

            case "t":
                return self.decode(self.data, lang=lang, mode="accessible")

            case _:
                return super().__format__(format_spec)

    @staticmethod
    def decode(data: bytes, *, lang: str = "en", mode: str = "display") -> str | bytes:
        """
        Decodes a byte stream into a string of tokens

        Each token is represented using one of three different representations formats, dictated by ``mode``:
            - ``display``: Represents the tokens with Unicode characters matching the calculator's display
            - ``accessible``: Represents the tokens with ASCII-only equivalents, often requiring multi-character glyphs
            - ``ti_ascii``: Represents the tokens with their internal font indices (returns a ``bytes`` object)

        :param data: The bytes to decode
        :param lang: The language used in ``string`` (defaults to English, ``en``)
        :param mode: The form of token representation to use for output (defaults to ``display``)
        :return: A string of token representations
        """

        return decode(data, lang=lang, mode=mode)[0]

    @staticmethod
    def encode(string: str, *, model: TIModel = None, lang: str = None) -> bytes:
        """
        Encodes a string of token represented in text into a byte stream

        :param string: The tokens to encode
        :param model: The model to target when encoding (defaults to no specific model)
        :param lang: The language used in ``string`` (defaults to English, ``en``)
        :return: A stream of token bytes
        """

        model = model or TI_84PCE
        return encode(string, model.get_trie(lang))[0]

    def get_min_os(self, data: bytes = None) -> OsVersion:
        return decode(data or self.data)[1]

    def get_version(self, data: bytes = None) -> int:
        match self.get_min_os(data):
            case os if os >= TI_84PCE.OS("5.3"):
                version = 0x0C

            case os if os >= TI_84PCE.OS("5.2"):
                version = 0x0B

            case os if os >= TI_84PCSE.OS("4.0"):
                version = 0x0A

            case os if os >= TI_84P.OS("2.55"):
                version = 0x07

            case os if os >= TI_84P.OS("2.53"):
                version = 0x06

            case os if os >= TI_84P.OS("2.30"):
                version = 0x05

            case os if os >= TI_84P.OS("2.21"):
                version = 0x04

            case os if os >= TI_83P.OS("1.16"):
                version = 0x03

            case os if os >= TI_83P.OS("1.15"):
                version = 0x02

            case os if os >= TI_83P.OS("1.00"):
                version = 0x01

            case _:
                version = 0x00

        if any(token in (data or self.data) for token in self.clock_tokens):
            version += 0x20

        return version

    @Loader[ByteString, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        try:
            if self.version != (version := self.get_version()):
                warn(f"The version is incorrect (expected 0x{version:02x}, got 0x{self.version:02x}).",
                     BytesWarning)

        except ValueError as e:
            warn(f"The file contains an invalid token {' '.join(str(e).split()[2:])}.",
                 BytesWarning)

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None, lang: str = None):
        self.data = self.encode(string, model=model, lang=lang)

    def string(self) -> str:
        return format(self, "")


class EquationName(TokenizedString):
    """
    Converter for the name section of equations

    Equation names can be any of the following:

    - ``Y1`` - ``Y0``
    - ``X1T`` - ``X6T``
    - ``Y1T`` - ``Y6T``
    - ``r1`` - ``r6``
    - ``u``, ``v``, or ``w``.
    """

    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        """
        Converts ``bytes`` -> ``str`` as done by the memory viewer

        :param data: The raw bytes to convert
        :return: The equation name contained in ``data``
        """

        varname = super().get(data)

        if varname.startswith("|"):
            return varname[1:]

        else:
            return varname.upper().strip("{}")

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        """
        Converts ``str`` -> ``bytes`` to match appearance in the memory viewer

        :param value: The value to convert
        :return: The name encoding of ``value``
        """

        varname = value[:8].lower()

        if varname.startswith("|") or varname in ("u", "v", "w"):
            varname = "|" + varname[-1]

        elif varname[0] != "{" and varname[-1] != "}":
            varname = "{" + varname + "}"

        return super().set(varname)


class TIEquation(TokenizedEntry, register=True):
    """
    Parser for equations

    A `TIEquation` is a stream of tokens that is evaluated either for graphing or on the homescreen.
    """

    extensions = {
        None: "8xy",
        TI_82: "82y",
        TI_83: "83y",
        TI_83P: "8xy"
    }

    _type_id = 0x03

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Y1",
                 version: int = None, archived: bool = None,
                 data: bytes = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, EquationName)
    def name(self) -> str:
        """
        The name of the entry

        Must be one of the equation names
        """


class TINewEquation(TIEquation, register=True):
    """
    Parser for internal equations

    A `TINewEquation` is simply a `TIEquation` with certain internal uses
    """

    _type_id = 0x0B


class TIString(TokenizedEntry, register=True):
    """
    Parser for strings

    A `TIString` is a stream of tokens.
    """

    extensions = {
        None: "8xs",
        TI_82: "82s",
        TI_83: "83s",
        TI_83P: "8xs"
    }

    _type_id = 0x04

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Str1",
                 version: int = None, archived: bool = None,
                 data: bytes = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None):
        super().load_string(string.strip("\"'"))

    def string(self) -> str:
        return f"\"{super().string()}\""


class TIProgram(TokenizedEntry, register=True):
    """
    Parser for programs

    A `TIProgram` is a stream of tokens that is run as a TI-BASIC program.
    """

    extensions = {
        None: "8xp",
        TI_82: "82p",
        TI_83: "83p",
        TI_83P: "8xp"
    }

    is_protected = False
    """
    Whether this program type is protected
    """

    _type_id = 0x05

    @Section(8, TokenizedString)
    def name(self, value) -> str:
        """
        The name of the entry

        Names must 1 to 8 characters in length.
        The name can include any characters A-Z, 0-9, or θ.
        The name cannot start with a digit.
        """

        varname = value[:8].upper()
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "θ", varname)
        varname = re.sub(r"[^θa-zA-Z0-9]", "", varname)

        if not varname or varname[0].isnumeric():
            warn(f"Var has invalid name: {varname}.",
                 BytesWarning)

        return varname

    def protect(self):
        """
        Cast this program to a protected program
        """

        self.type_id = 0x06
        self.coerce()

    def unprotect(self):
        """
        Cast this program to an unprotected program
        """

        self.type_id = 0x05
        self.coerce()


class TIProtectedProgram(TIProgram, register=True):
    """
    Parser for protected programs

    A `TIProtectedProgram` is a `TIProgram` with protection against editing.
    """

    is_protected = True

    _type_id = 0x06


__all__ = ["TIEquation", "TINewEquation", "TIString", "TIProgram", "TIProtectedProgram"]
