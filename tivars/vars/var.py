import re

from collections import namedtuple
from typing import BinaryIO


from tivars.models import *


class TIHeader(namedtuple("TIHeader", ["signature", "export", "comment", "entry_length"])):
    __slots__ = ()

    def dump(self) -> bytearray:
        dump = bytearray()

        dump.extend(self.signature)
        dump.extend(self.export)
        dump.extend(self.comment.encode('utf8').ljust(42, b'\x00'))
        dump.extend(self.entry_length.to_bytes(2, 'little'))

        return dump


class TIEntry(namedtuple("TIEntry", ["meta_length", "data_length", "type_id", "name", "version", "archived", "data"])):
    base_meta_length = 0x0B
    flash_meta_length = 0x0D

    __slots__ = ()

    @property
    def flash_bytes(self) -> int:
        return self.meta_length - TIEntry.base_meta_length

    @property
    def varname(self) -> bytearray:
        varname = self.name
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "[", varname)
        varname = re.sub(r"[^[a-zA-Z0-9]", "", varname)

        if not varname or varname[0].isnumeric():
            raise ValueError(f"Var has invalid name: {self.name}")

        return bytearray(varname.ljust(8, '\0')[:8].upper().encode('utf8'))

    def dump(self) -> bytearray:
        dump = bytearray()

        dump.extend(self.meta_length.to_bytes(2, 'little'))
        dump.extend(self.data_length.to_bytes(2, 'little'))
        dump.extend(self.type_id)
        dump.extend(self.varname)

        if self.flash_bytes:
            dump.extend(self.version)
            dump.append(self.archived)

        dump.extend(self.data_length.to_bytes(2, 'little'))
        dump.extend(self.data)

        return dump


class TIVar:
    extensions = {}
    type_id = None

    _type_ids = {}

    def __init__(self, name: str = "MyVar", model: 'TIModel' = TI_84p):
        self.model = model

        self.signature = model.signature
        self.export = b'\x1A\x0A\x00'
        self.comment = "Created by tivars_lib_py"

        self.meta_length = TIEntry.flash_meta_length if model.has(TIFeatures.FLASH) else TIEntry.base_meta_length

        self.name = name

        self.version = b'\x00'
        self.archived = False

        self.data = bytearray()

        self.corrupt = False

    @property
    def checksum(self) -> int:
        checksum = 0
        checksum += self.meta_length
        checksum += int.from_bytes(self.type_id, 'little')
        checksum += 2 * sum(self.data_length.to_bytes(2, 'little'))
        checksum += sum(self.varname)
        checksum += sum(self.data)

        if self.flash_bytes:
            checksum += int.from_bytes(self.version, 'little')
            checksum += self.archived

        return checksum & 0xFFFF

    @property
    def data_length(self) -> int:
        return len(self.data)

    @property
    def entry(self) -> 'TIEntry':
        return TIEntry(meta_length=self.meta_length,
                       data_length=self.data_length,
                       type_id=self.type_id,
                       name=self.name,
                       version=self.version,
                       archived=self.archived,
                       data=self.data)

    @property
    def entry_length(self) -> int:
        return 2 + 2 + self.meta_length + self.data_length

    @property
    def extension(self) -> str:
        return self.extensions[self.model]

    @property
    def header(self) -> 'TIHeader':
        return TIHeader(signature=self.signature,
                        export=self.export,
                        comment=self.comment,
                        entry_length=self.entry_length)

    @property
    def flash_bytes(self) -> int:
        return self.entry.flash_bytes

    @property
    def varname(self) -> bytearray:
        return self.entry.varname

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
            var = TIVar._type_ids[type_id](model)
        except KeyError:
            raise ValueError("File has unknown type ID.")

        file.seek(0)
        var.load(file)
        return var

    @staticmethod
    def register(var_type: type['TIVar']):
        TIVar._type_ids[var_type.type_id] = var_type

    def archive(self):
        if self.model.has(TIFeatures.FLASH):
            self.archived = True
        else:
            raise TypeError("Calculator model does not support archiving.")

    def dump(self) -> bytearray:
        return self.header.dump() + self.entry.dump() + self.checksum.to_bytes(2, 'little')

    def dumps(self) -> str:
        pass

    def load(self, file: BinaryIO, strict=True):
        self.signature = file.read(8)
        self.export = file.read(3)
        self.comment = file.read(42).decode('utf8')
        entry_length = int.from_bytes(file.read(2), 'little')

        self.meta_length = int.from_bytes(file.read(2), 'little')
        data_length = int.from_bytes(file.read(2), 'little')

        type_id = file.read(1)
        if type_id != self.type_id:
            if strict:
                raise TypeError("The var type is incorrect. Use TIVar.infer if you don't know the type.")
            else:
                self.corrupt = True

        self.name = file.read(8).decode('utf8')

        if self.meta_length == TIEntry.flash_meta_length:
            self.version = file.read(1)
            self.archived = bool(file.read(1))

        elif self.meta_length != TIEntry.base_meta_length:
            if strict:
                raise ValueError("The var entry meta length has an unexpected value.")
            else:
                self.corrupt = True

        data_length2 = int.from_bytes(file.read(2), 'little')
        if data_length != data_length2:
            if strict:
                raise ValueError("The var entry data lengths are mismatched.")
            else:
                self.corrupt = True

        self.data = file.read(data_length)

        if entry_length != self.entry_length:
            if strict:
                raise ValueError("The var entry length is incorrect.")
            else:
                self.corrupt = True

    def loads(self, string: str):
        pass

    def unarchive(self):
        if self.model.has(TIFeatures.FLASH):
            self.archived = False
        else:
            raise TypeError("Calculator model does not support archiving.")


__all__ = ["TIHeader", "TIEntry", "TIVar"]
