import io
import re

from typing import ByteString
from warnings import warn

from tivars.models import *
from tivars.tokenizer import encode, decode
from tivars.tokenizer.tokens import *
from ..data import *
from ..var import SizedEntry


class TokenizedEntry(SizedEntry):
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

    clock_tokens = [
        b'\xEF\x00', b'\xEF\x01', b'\xEF\x02', b'\xEF\x03', b'\xEF\x04',
        b'\xEF\x07', b'\xEF\x08', b'\xEF\x09', b'\xEF\x0A', b'\xEF\x0B', b'\xEF\x0C', b'\xEF\x0D',
        b'\xEF\x0E', b'\xEF\x0F', b'\xEF\x10'
    ]

    def derive_version(self) -> bytes:
        def has_bytes_in(prefix: bytes, start: int, end: int):
            return any(prefix + int.to_bytes(byte, 1, 'little') in self.raw.data for byte in range(start, end + 1))

        version = 0x00
        match self.raw.data:
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

        if any(token in self.raw.data for token in self.clock_tokens):
            version += 0x20

        return int.to_bytes(version, 1, 'little')

    def decode(self, data: bytearray, *, model: TIModel = None) -> str:
        byte_map = self.tokens[model or TI_84PCEPY][1]
        return decode(data, byte_map)

    def encode(self, string: str, *, model: TIModel = None) -> bytes:
        token_map = self.tokens[model or TI_84PCEPY][0]
        return encode(string, token_map)

    def load_bytes(self, data: ByteString):
        super().load_bytes(data)

        if self.raw.version != (version := self.derive_version()):
            warn(f"The version is incorrect (expected {version}, got {self.raw.version}).",
                 BytesWarning)

    def load_data_section(self, data: io.BytesIO):
        data_length = int.from_bytes(length_bytes := data.read(2), 'little')
        self.raw.data = bytearray(length_bytes + data.read(data_length))

    def load_string(self, string: str, *, model: TIModel = None):
        self.raw.data[2:] = self.encode(string, model=model)
        self.length = len(self.raw.data[2:])
        self.raw.version = self.derive_version()

    def string(self) -> str:
        return self.decode(self.data[2:])


class TIEquation(TokenizedEntry):
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

    _type_id = b'\x03'


class TIString(TokenizedEntry):
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

    _type_id = b'\x04'

    def load_string(self, string: str, *, model: TIModel = None):
        super().load_string(string.strip("\"'"))

    def string(self) -> str:
        return f"\"{super().string()}\""


class TIProgram(TokenizedEntry):
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

    _type_id = b'\x05'

    @Section(8, String)
    def name(self, value) -> str:
        """
        The name of the entry

        Must be 1 to 8 characters in length
        Can include any characters A-Z, 0-9, or Θ
        Cannot start with a digit
        """

        varname = value[:8].upper()
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "[", varname)
        varname = re.sub(r"[^[a-zA-Z0-9]", "", varname)

        if not varname or varname[0].isnumeric():
            warn(f"Var has invalid name: {varname}.",
                 BytesWarning)

        return varname

    @property
    def is_protected(self) -> bool:
        return False


class TIProtectedProgram(TIProgram):
    _type_id = b'\x06'

    @property
    def is_protected(self) -> bool:
        return True


__all__ = ["TIEquation", "TIString", "TIProgram", "TIProtectedProgram"]
