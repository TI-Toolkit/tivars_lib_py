import io

from warnings import warn

from tivars.models import *
from .buffer import *


class TIHeader(Section):
    magic = StringBuffer(8)
    extra = Buffer(2)
    product_id = Buffer(1)
    comment = StringBuffer(42)

    size = 55

    def __init__(self,
                 magic: str = "**TI83F*",
                 extra: bytes = b'\x1A\x0A',
                 product_id: bytes = b'\x00',
                 comment: str = "Created by tivars_lib_py",
                 entry_length: int = 0):
        self.magic = magic
        self.extra = extra
        self.product_id = product_id
        self.comment = comment
        self._entry_length = entry_length

    def bytes(self) -> bytes:
        dump = b''

        dump += self.magic_bytes
        dump += self.extra
        dump += self.product_id
        dump += self.comment_bytes
        dump += self.entry_length_bytes

        return dump

    @property
    def entry_length(self) -> int:
        return self._entry_length

    @property
    def entry_length_bytes(self) -> bytes:
        return int.to_bytes(self._entry_length, 2, 'little')

    def load_bytes(self, data: bytes):
        data = io.BytesIO(data)

        self.magic_bytes = data.read(8)
        self.extra_bytes = data.read(2)
        self.product_id_bytes = data.read(1)
        self.comment_bytes = data.read(42)
        self._entry_length = int.from_bytes(data.read(2), 'little')

    def load_string(self, string: str):
        raise NotImplementedError

    def string(self) -> str:
        raise NotImplementedError


class TIEntry(Section):
    base_meta_length = 0x0B
    flash_meta_length = 0x0D

    meta_length = IntBuffer(2)
    name = NameBuffer(8)
    version = Buffer(1)
    archived = BoolBuffer()
    data = Buffer()

    def __init__(self,
                 meta_length: int = 0x0D,
                 type_id: bytes = b'\x00',
                 name: str = "UNNAMED",
                 version: bytes = b'\x00',
                 archived: bool = False,
                 data: bytearray = bytearray()):
        self.meta_length = meta_length
        self.type_id = type_id
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

    def bytes(self) -> bytes:
        dump = b''

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

    def load_bytes(self, data: bytes, *, offset: bool = False):
        data = io.BytesIO(data)

        if offset:
            data.read(TIHeader.size)

        self.meta_length_bytes = data.read(2)
        data_length = int.from_bytes(data.read(2), 'little')

        self.type_id = data.read(1)
        self.name_bytes = data.read(8)

        if self.meta_length == TIEntry.flash_meta_length:
            self.version = data.read(1)
            self.archived_bytes = data.read(1)

        elif self.meta_length != TIEntry.base_meta_length:
            warn(f"The entry meta length has an unexpected value ({self.meta_length}).",
                 BytesWarning)

        data_length2 = int.from_bytes(data.read(2), 'little')
        if data_length != data_length2:
            warn(f"The var entry data lengths are mismatched ({data_length} vs. {data_length2}).",
                 BytesWarning)

        self.data = bytearray(data.read(data_length))

        checksum = int.from_bytes(data.read(2), 'little')
        if checksum != self.checksum:
            warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                 BytesWarning)

    def load_string(self, string: str):
        raise NotImplementedError

    def string(self) -> str:
        raise NotImplementedError


class TIVar(TIHeader, TIEntry):
    extensions = {}
    type_ids = {}

    type_id = None

    def __init__(self, *, name: str = 'UNNAMED', model: 'TIModel' = None, default_product_id: bool = False):
        magic = "**TI83F*" if model is None else model.magic
        product_id = b'\x00' if default_product_id or model is None else model.product_id

        meta_length = TIEntry.flash_meta_length if \
            model is None or model.has(TIFeature.FLASH) else TIEntry.base_meta_length

        super().__init__(magic=magic, product_id=product_id)
        super(TIHeader, self).__init__(meta_length=meta_length,
                                       type_id=self.type_id,
                                       name=name)
        self.model = model

    @property
    def entry(self) -> 'TIEntry':
        return TIEntry(self.meta_length, self.type_id, self.name, self.version, self.archived, self.data)

    @property
    def entry_length(self) -> int:
        return TIEntry.entry_length.__get__(self)

    @property
    def extension(self) -> str:
        try:
            return self.extensions[self.model]

        except KeyError:
            warn(f"Model {self.model} not recognized.")
            return self.extensions[None]

    @property
    def header(self) -> 'TIHeader':
        return TIHeader(self.magic, self.extra, self.product_id, self.comment, self.entry_length)

    @staticmethod
    def register(var_type: type['TIVar']):
        TIVar.type_ids[var_type.type_id] = var_type

    def archive(self):
        if self.model is None or self.model.has(TIFeature.FLASH):
            self.archived = True
        else:
            raise TypeError(f"The {self.model} does not support archiving.")

    def bytes(self) -> bytes:
        return self.header.bytes() + self.entry.bytes()

    def load_bytes(self, data: bytes):
        super().load_bytes(data)

        match self.magic:
            case TI_82.magic:
                model = TI_82
            case TI_83.magic:
                model = TI_83
            case TI_84P.magic:
                try:
                    models = [m for m in MODELS if m.magic == self.magic]
                    if self.product_id != b'\x00':
                        models = [m for m in models if m.product_id == self.product_id]

                    model = max(models, key=lambda m: m.flags)

                except ValueError:
                    warn(f"The var product id is not recognized ({self.product_id}).",
                         BytesWarning)
                    model = None

            case _:
                warn(f"The var file magic is not recognized ({self.magic}).",
                     BytesWarning)
                model = None

        if self.model is None:
            self.model = model

        elif self.model != model:
            warn(f"The var file comes from a different model (expected {self.model}, got {model}).")

        data = io.BytesIO(data)
        data.read(TIHeader.size)

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
                warn(f"The var contains flash bytes, but the {self.model} does not have a flash chip.",
                     BytesWarning)

            self.version = data.read(1)
            self.archived_bytes = data.read(1)

        elif self.meta_length == TIVar.base_meta_length:
            if self.model is not None and self.model.has(TIFeature.FLASH):
                warn(f"The var doesn't contain flash bytes, but the {self.model} uses a flash chip.",
                     BytesWarning)

        elif self.meta_length != TIVar.base_meta_length:
            warn(f"The var entry meta length has an unexpected value ({self.meta_length}).",
                 BytesWarning)

            if self.model is not None:
                if self.model.has(TIFeature.FLASH):
                    self.version = data.read(1)
                    self.archived_bytes = data.read(1)

        data_length2 = int.from_bytes(data.read(2), 'little')
        if data_length != data_length2:
            warn(f"The var entry data lengths are mismatched ({data_length} vs. {data_length2}).",
                 BytesWarning)

        self.data = bytearray(data.read(data_length))
        if self._entry_length != self.entry_length:
            warn(f"The var entry length is incorrect (expected {self.entry_length}, got {self._entry_length}).",
                 BytesWarning)

        checksum = int.from_bytes(data.read(2), 'little')
        if checksum != self.checksum:
            warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                 BytesWarning)

    def load_string(self, string: str):
        raise NotImplementedError

    def open(self, filename: str):
        if not any(filename.endswith(extension) for extension in self.extensions.values()):
            warn(f"File extension .{filename.split('.')[-1]} not recognized for var type {type(self)}; "
                 f"attempting to read anyway.")

        elif self.model is not None and not filename.endswith(self.extension):
            warn(f"Var type {type(self)} on the {self.model} uses .{self.extension} extension.")

        super().open(filename)

    def save(self, filename: str = None):
        super().save(filename or f"{self.name}.{self.extension}")

    def string(self) -> str:
        raise NotImplementedError

    def unarchive(self):
        if self.model is None or self.model.has(TIFeature.FLASH):
            self.archived = False
        else:
            raise TypeError(f"The {self.model} does not support archiving.")


__all__ = ["TIHeader", "TIEntry", "TIVar"]
