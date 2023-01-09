import warnings

from typing import BinaryIO, Iterator

from tivars.models import *
from .buffer import *


class TIHeader(Section):
    signature = StringBuffer(8, "**TI83F*")
    export = Buffer(3, b'\x1A\x0A\x00')
    comment = StringBuffer(42, "Created by tivars_lib_py")
    entry_length = IntBuffer(2)


class TIEntry(Section):
    base_meta_length = 0x0B
    flash_meta_length = 0x0D

    meta_length = IntBuffer(2)
    data_length = IntBuffer(2)
    type_id = Buffer(1)
    name = NameBuffer(8, "UNNAMED")
    version = Buffer(1)
    archived = BoolBuffer()
    data_length2 = IntBuffer(2)
    data = Buffer()
    checksum = IntBuffer(2)

    @property
    def flash_bytes(self) -> bytes:
        return (self.version + bytes([self.archived]))[:self.meta_length - TIEntry.base_meta_length]


class TIVar(TIHeader, TIEntry):
    extensions = {}

    _type_ids = {}

    def __init__(self, *, model: 'TIModel' = None):
        super().__init__()

        self.model = model

        self.corrupt = False

    @property
    def checksum(self) -> int:
        checksum = 0
        checksum += self.meta_length
        checksum += self.type_id
        checksum += 2 * sum(self.data_length.to_bytes(2, 'little'))
        checksum += sum(self.name)
        checksum += sum(self.data)

        if self.flash_bytes:
            checksum += self.version
            checksum += self.archived

        return checksum & 0xFFFF

    @property
    def data_length(self) -> int:
        return len(self.data)

    @property
    def entry_length(self) -> int:
        return 2 + 2 + self.meta_length + self.data_length

    @property
    def extension(self) -> str:
        return self.extensions[self.model]

    @staticmethod
    def infer(file: BinaryIO, model: 'TIModel' = None) -> 'TIVar':
        signature = file.read(8)

        if model is None:
            match signature:
                case TI_82.signature: model = TI_82
                case TI_83.signature: model = TI_83
                case TI_84p.signature: model = TI_84p
                case _:
                    raise ValueError("File has unknown model signature.")

        file.read(51)

        type_id = file.read(1)
        try:
            var = TIVar._type_ids[type_id](file.name, model)
        except KeyError:
            raise ValueError("File has unknown type ID.")

        file.seek(0)
        var.load_file(file)
        return var

    @staticmethod
    def register(var_type: type['TIVar']):
        TIVar._type_ids[var_type.type_id] = var_type

    def archive(self):
        if self.model is not None and self.model.has(TIFeature.FLASH):
            self.archived = True
        else:
            raise TypeError("Calculator model does not support archiving.")

    def load_bytes(self, data: bytes | Iterator[bytes]):
        data = iter(data)

        self.load_buffer(self.signature, data)
        self.load_buffer(self.export, data)
        self.load_buffer(self.comment, data)
        self.load_buffer(self.entry_length, data)

        self.load_buffer(self.meta_length, data)
        self.load_buffer(self.data_length, data)

        if self.entry_length != (entry_length := 2 + 2 + self.meta_length + self.data_length):
            warnings.warn(f"The var entry length is incorrect (expected {entry_length}, got {self.entry_length}).",
                          BytesWarning)
            self.corrupt = True

        if next(data) != self.type_id:
            raise TypeError("The var type is incorrect. Use TIVar.infer if you don't know the type.")

        self.load_buffer(self.name, data)

        if self.meta_length == TIVar.flash_meta_length:
            self.load_buffer(self.version, data)
            self.load_buffer(self.archived, data)

        elif self.meta_length != TIVar.base_meta_length:
            warnings.warn(f"The var entry meta length has an unexpected value (0x{self.meta_length:x}).",
                          BytesWarning)
            self.corrupt = True

        self.load_buffer(self.data_length2, data)
        if self.data_length != self.data_length2:
            warnings.warn(f"The var entry data lengths are mismatched ({self.data_length} vs. {self.data_length2}).",
                          BytesWarning)
            self.corrupt = True

        self.load_buffer(self.data, data, self.data_length2)
        self.load_buffer(self.checksum, data)

    def save(self, filename: str = None):
        super().save(filename or f"{self.name}.{self.extension}")

    def unarchive(self):
        if self.model is not None and self.model.has(TIFeature.FLASH):
            self.archived = False
        else:
            raise TypeError("Calculator model does not support archiving.")


__all__ = ["TIHeader", "TIEntry", "TIVar"]
