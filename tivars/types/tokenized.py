from warnings import warn

from tivars.models import *
from tivars.tokenizer import encode, decode
from tivars.tokenizer.tokens import *
from ..var import TIEntry


class TokenizedVar(TIEntry):
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

    versions = [
        b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06',
        b'\x0A', b'\x0B', b'\x0C',
        b'\x20', b'\x21', b'\x22', b'\x23', b'\x24', b'\x25', b'\x26',
        b'\x2A', b'\x2B', b'\x2C'
    ]

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

        version = 0x0
        match self.raw.data:
            case _TI_84PCE if has_bytes_in(b'\xEF', 0x9E, 0xA6):
                version = 0xC

            case _TI_84PCE if has_bytes_in(b'\xEF', 0x73, 0x98):
                version = 0xB

            case _TI_84PCSE if has_bytes_in(b'\xEF', 0x41, 0x6C):
                version = 0xA

            case _TI_84P if has_bytes_in(b'\xEF', 0x17, 0x3D):
                version = 0x6

            case _TI_84P if has_bytes_in(b'\xEF', 0x13, 0x16):
                version = 0x5

            case _TI_84P if has_bytes_in(b'\xEF', 0x00, 0x12):
                version = 0x4

            case _TI_83P if has_bytes_in(b'\xBB', 0xDB, 0xF5):
                version = 0x3

            case _TI_83P if has_bytes_in(b'\xBB', 0xCF, 0xDA):
                version = 0x2

            case _TI_83P if has_bytes_in(b'\xBB', 0x68, 0xCE):
                version = 0x1

        if any(token in self.raw.data for token in self.clock_tokens):
            version += 0x20

        return int.to_bytes(version, 1, 'little')

    def load_bytes(self, data: bytes):
        super().load_bytes(data)

        if self.raw.version != (version := self.derive_version()):
            warn(f"The version is incorrect (expected {version}, got {self.raw.version}).",
                 BytesWarning)

    def load_string(self, string: str, *, model: TIModel = None):
        token_map = self.tokens[model or TI_84PCEPY][0]
        self.raw.data = encode(string, token_map)
        self.raw.version = self.derive_version()

    def string(self) -> str:
        byte_map = self.tokens[TI_84PCEPY][1]
        return decode(self.data, byte_map)


class TIEquation(TokenizedVar):
    _type_id = b'\x03'


class TIString(TokenizedVar):
    _type_id = b'\x04'

    def load_string(self, string: str, *, model: TIModel = None):
        super().load_string(string.strip("\"'"))

    def string(self) -> str:
        return f"\"{super().string()}\""


class TIProgram(TokenizedVar):
    _type_id = b'\x05'

    @property
    def is_protected(self) -> bool:
        return False


class TIProtectedProgram(TIProgram):
    _type_id = b'\x06'

    @property
    def is_protected(self) -> bool:
        return True


__all__ = ["TIEquation", "TIString", "TIProgram", "TIProtectedProgram"]
