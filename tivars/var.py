import io
import warnings

from tivars.models import *
from .buffer import *


class TIHeader(Section):
    signature = StringBuffer(8)
    export = Buffer(3)
    comment = StringBuffer(42)

    def __init__(self,
                 signature: str = "**TI83F*",
                 export: bytes = b'\x1A\x0A\x00',
                 comment: str = "Created by tivars_lib_py",
                 entry_length: int = 0):
        self.signature = signature
        self.export = export
        self.comment = comment
        self._entry_length = entry_length


class TIEntry(Section):
    base_meta_length = 0x0B
    flash_meta_length = 0x0D

    type_id = None

    meta_length = IntBuffer(2)
    name = NameBuffer(8)
    version = Buffer(1)
    archived = BoolBuffer()
    data = Buffer()

    def __init__(self,
                 meta_length: int = 0x0D,
                 name: str = "UNNAMED",
                 version: bytes = b'\x00',
                 archived: bool = False,
                 data: bytearray = bytearray()):
        self.meta_length = meta_length
        self.name = name
        self.version = version
        self.archived = archived
        self.data = data

    @property
    def checksum(self) -> int:
        checksum = 0
        checksum += self.meta_length
        checksum += int.from_bytes(self.type_id, 'little')
        checksum += 2 * sum(self.data_length.to_bytes(2, 'little'))
        checksum += sum(self.name_bytes)
        checksum += sum(self.data)

        if self.flash_bytes:
            checksum += int.from_bytes(self.version, 'little')
            checksum += self.archived

        return checksum & 0xFFFF

    @property
    def checksum_bytes(self) -> bytes:
        return int.to_bytes(self.checksum, 2, 'little')

    @property
    def data_length(self) -> int:
        return len(self.data)

    @property
    def data_length_bytes(self) -> bytes:
        return int.to_bytes(self.data_length, 2, 'little')

    @property
    def entry_length(self) -> int:
        return 2 + 2 + self.meta_length + self.data_length

    @property
    def entry_length_bytes(self) -> bytes:
        return int.to_bytes(self.entry_length, 2, 'little')

    @property
    def flash_bytes(self) -> bytes:
        return (self.version + bytes([self.archived]))[:self.meta_length - TIEntry.base_meta_length]


class TIVar(TIHeader, TIEntry):
    extensions = {}
    type_ids = {}

    def __init__(self, *, name: str = 'UNNAMED', model: 'TIModel' = None):
        signature = "**TI83F*" if model is None else model.signature

        meta_length = TIEntry.flash_meta_length if \
            model is None or model.has(TIFeature.FLASH) else TIEntry.base_meta_length

        super().__init__(signature=signature)
        super(TIHeader, self).__init__(meta_length=meta_length,
                                       name=name)
        self.model = model

    @property
    def entry(self) -> 'TIEntry':
        return TIEntry(self.meta_length, self.name, self.version, self.archived, self.data)

    @property
    def extension(self) -> str:
        return self.extensions[self.model]

    @property
    def header(self) -> 'TIHeader':
        return TIHeader(self.signature, self.export, self.comment, self.entry_length)

    @staticmethod
    def register(var_type: type['TIVar']):
        TIVar.type_ids[var_type.type_id] = var_type

    def archive(self):
        if self.model is None or self.model.has(TIFeature.FLASH):
            self.archived = True
        else:
            raise TypeError(f"The {self.model} does not support archiving.")

    def bytes(self) -> bytes:
        dump = b''

        dump += self.signature_bytes
        dump += self.export
        dump += self.comment_bytes
        dump += self.entry_length_bytes

        dump += self.meta_length_bytes
        dump += self.data_length_bytes
        dump += self.type_id
        dump += self.name_bytes

        if self.flash_bytes:
            dump += self.version
            dump += self.archived_bytes

        dump += self.data_length_bytes
        dump += self.data
        dump += self.checksum_bytes

        return dump

    def load_bytes(self, data: bytes):
        data = io.BytesIO(data)

        self.signature_bytes = data.read(8)
        match self.signature:
            case TI_82.signature:
                model = TI_82
            case TI_83.signature:
                model = TI_83
            case TI_84p.signature:
                model = TI_84pcepy
            case _:
                raise warnings.warn(f"The var signature is not recognized ({self.signature}).",
                                    BytesWarning)

        if self.model is None:
            self.model = model

        self.export_bytes = data.read(3)
        self.comment_bytes = data.read(42)
        entry_length = int.from_bytes(data.read(2), 'little')

        self.meta_length_bytes = data.read(2)
        data_length = int.from_bytes(data.read(2), 'little')

        type_id = data.read(1)
        if self.type_id is None:
            try:
                self.__class__ = TIVar.type_ids[type_id]

            except KeyError:
                raise TypeError(f"Type id 0x{type_id:x} is not recognized.")

        elif type_id != self.type_id:
            raise TypeError("The var type is incorrect. Use a TIVar instance if you don't know the type.")

        self.name_bytes = data.read(8)

        if self.meta_length == TIVar.flash_meta_length:
            if self.model is not None and not self.model.has(TIFeature.FLASH):
                warnings.warn(f"The var contains flash bytes, but the {self.model} does not have a flash chip.",
                              BytesWarning)

            self.version = data.read(1)
            self.archived_bytes = data.read(1)

        elif self.meta_length == TIVar.base_meta_length:
            if self.model is not None and self.model.has(TIFeature.FLASH):
                warnings.warn(f"The var doesn't contain flash bytes, but the {self.model} uses a flash chip.",
                              BytesWarning)

        elif self.meta_length != TIVar.base_meta_length:
            warnings.warn(f"The var entry meta length has an unexpected value ({self.meta_length}).",
                          BytesWarning)

            if self.model is not None:
                if self.model.has(TIFeature.FLASH):
                    self.version = data.read(1)
                    self.archived_bytes = data.read(1)

        data_length2 = int.from_bytes(data.read(2), 'little')
        if data_length != data_length2:
            warnings.warn(f"The var entry data lengths are mismatched ({data_length} vs. {data_length2}).",
                          BytesWarning)

        self.data = bytearray(data.read(data_length))
        if entry_length != self.entry_length:
            warnings.warn(f"The var entry length is incorrect (expected {self.entry_length}, got {entry_length}).",
                          BytesWarning)

        checksum = int.from_bytes(data.read(2), 'little')
        if checksum != self.checksum:
            warnings.warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                          BytesWarning)

    def save(self, filename: str = None):
        super().save(filename or f"{self.name}.{self.extension}")

    def unarchive(self):
        if self.model is None or self.model.has(TIFeature.FLASH):
            self.archived = False
        else:
            raise TypeError(f"The {self.model} does not support archiving.")


__all__ = ["TIHeader", "TIEntry", "TIVar"]
