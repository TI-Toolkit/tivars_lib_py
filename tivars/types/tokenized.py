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
        b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06',
        b'\x0A', b'\x0B', b'\x0C',
        b'\x20', b'\x21', b'\x22', b'\x23', b'\x24', b'\x25', b'\x26',
        b'\x2A', b'\x2B', b'\x2C'
    ]

    min_data_length = 2

    tokens = {
        TI_82: (TI82_TOKENS, TI82_BYTES),
        TI_83: (TI83_TOKENS, TI83_BYTES),
        TI_82A: (TI83_TOKENS, TI83_BYTES),
        TI_83P: (TI83_TOKENS, TI83_BYTES),
        TI_84P: (TI83_TOKENS, TI83_BYTES),
        TI_84T: (TI83_TOKENS, TI83_BYTES),
        TI_84PCSE: (CSE_TOKENS, CSE_BYTES),
        TI_84PCE: (CE_TOKENS, CE_BYTES),
        TI_84PCEPY: (CE_TOKENS, CE_BYTES),
        TI_83PCE: (CE_TOKENS, CE_BYTES),
        TI_83PCEEP: (CE_TOKENS, CE_BYTES),
        TI_82AEP: (CE_TOKENS, CE_BYTES)
    }
    """
    Token mappings used for each model
    """

    clock_tokens = [
        b'\xEF\x00', b'\xEF\x01', b'\xEF\x02', b'\xEF\x03', b'\xEF\x04',
        b'\xEF\x07', b'\xEF\x08', b'\xEF\x09', b'\xEF\x0A', b'\xEF\x0B', b'\xEF\x0C', b'\xEF\x0D',
        b'\xEF\x0E', b'\xEF\x0F', b'\xEF\x10'
    ]
    """
    Tokens which interface with the RTC
    
    These tokens influence the entry's version, though detecting the presence of the RTC has no current application.
    """

    def derive_version(self) -> int:
        """
        Determines the version for this entry

        The version increments with the presence of tokens which indicate non-backwards compatible functionality.

        :return: This entry's version
        """

        def has_bytes_in(prefix: bytes, start: int, end: int):
            return any(prefix + bytes([byte]) in self.data for byte in range(start, end + 1))

        version = 0x00
        match self.data:
            case _TI_84PCE if has_bytes_in(b'\xEF', 0x9E, 0xA6):
                version = 0x0C

            case _TI_84PCE if has_bytes_in(b'\xEF', 0x73, 0x98):
                version = 0x0B

            case _TI_84PCSE if has_bytes_in(b'\xEF', 0x41, 0x6C):
                version = 0x0A

            case _TI_84P if has_bytes_in(b'\xEF', 0x17, 0x3D):
                version = 0x06

            case _TI_84P if has_bytes_in(b'\xEF', 0x13, 0x16):
                version = 0x05

            case _TI_84P if has_bytes_in(b'\xEF', 0x00, 0x12):
                version = 0x04

            case _TI_83P if has_bytes_in(b'\xBB', 0xDB, 0xF5):
                version = 0x03

            case _TI_83P if has_bytes_in(b'\xBB', 0xCF, 0xDA):
                version = 0x02

            case _TI_83P if has_bytes_in(b'\xBB', 0x68, 0xCE):
                version = 0x01

        if any(token in self.data for token in self.clock_tokens):
            version += 0x20

        return version

    def decode(self, data: bytearray, *, model: TIModel = None) -> str:
        """
        Decodes a byte stream into a string of tokens given a model

        :param data: The bytes to decode
        :param model: The targeted model
        :return: A string of token representations
        """

        byte_map = self.tokens[model or TI_84PCEPY][1]
        return decode(data, byte_map)

    def encode(self, string: str, *, model: TIModel = None) -> bytes:
        """
        Encodes a string of tokens into a byte stream given a model

        :param string: The tokens to encode
        :param model: The targeted model
        :return: A stream of token bytes
        """

        token_map = self.tokens[model or TI_84PCEPY][0]
        return encode(string, token_map)

    @Loader[ByteString, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        if self.version != (version := self.derive_version()):
            warn(f"The version is incorrect (expected 0x{version:02x}, got 0x{self.version:02x}).",
                 BytesWarning)

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None):
        self.data = self.encode(string, model=model)
        self.version = self.derive_version()

    def string(self) -> str:
        return self.decode(self.data)


class EquationName(TokenizedString):
    """
    Converter for the name section of equations

    Equation names can be any of `Y1` - `Y0`, `X1T` - `X6T`, `Y1T` - `Y6T`, `r1` - `r6`, `u`, `v`, or `w`.
    """

    _T = str

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        """
        Converts `bytes` -> `str` as done by the memory viewer

        :param data: The raw bytes to convert
        :return: The equation name contained in `data`
        """

        varname = super().get(data)

        if varname.startswith("|"):
            return varname[1:]

        else:
            return varname.upper().strip("{}")

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        """
        Converts `str` -> `bytes` to match appearance in the memory viewer

        :param value: The value to convert
        :return: The name encoding of `value`
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
        TI_82A: "8xy",
        TI_82P: "8xy",
        TI_83P: "8xy",
        TI_84P: "8xy",
        TI_84T: "8xy",
        TI_84PCSE: "8xy",
        TI_84PCE: "8xy",
        TI_84PCEPY: "8xy",
        TI_83PCE: "8xy",
        TI_83PCEEP: "8xy",
        TI_82AEP: "8xy"
    }

    _type_id = 0x03

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Y1",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, EquationName)
    def name(self) -> str:
        """
        The name of the entry

        Must be one of the equation names: `Y1` - `Y0`, `X1T` - `X6T`, `Y1T` - `Y6T`, `r1` - `r6`, `u`, `v`, or `w`
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
        TI_82A: "8xs",
        TI_82P: "8xs",
        TI_83P: "8xs",
        TI_84P: "8xs",
        TI_84T: "8xs",
        TI_84PCSE: "8xs",
        TI_84PCE: "8xs",
        TI_84PCEPY: "8xs",
        TI_83PCE: "8xs",
        TI_83PCEEP: "8xs",
        TI_82AEP: "8xs"
    }

    _type_id = 0x04

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Str1",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):

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
        TI_82A: "8xp",
        TI_82P: "8xp",
        TI_83P: "8xp",
        TI_84P: "8xp",
        TI_84T: "8xp",
        TI_84PCSE: "8xp",
        TI_84PCE: "8xp",
        TI_84PCEPY: "8xp",
        TI_83PCE: "8xp",
        TI_83PCEEP: "8xp",
        TI_82AEP: "8xp"
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


class TIProtectedProgram(TIProgram, register=True):
    """
    Parser for protected programs

    A `TIProtectedProgram` is a `TIProgram` with protection against editing.
    """

    is_protected = True

    _type_id = 0x06


__all__ = ["TIEquation", "TINewEquation", "TIString", "TIProgram", "TIProtectedProgram"]
