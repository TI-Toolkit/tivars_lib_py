import io
import re

from typing import BinaryIO
from warnings import warn

from tivars.models import *
from .byteview import *


class TIVar(ByteArray):
    extensions = {}
    type_ids = {}

    _type_id = None

    base_meta_length = 11
    flash_meta_length = 13

    @byteview()[:55]
    def header(self):
        """
        The header section of the var

        Contains the file magic, export bytes, product ID, comment, and entry length
        """
        pass

    @byteview()[55:-2]
    def entry(self):
        """
        The entry section of the var

        Contains the meta length, meta section, data length, and data section
        """
        pass

    @byteview()[-2:]
    def checksum(self):
        """
        The checksum for the var

        This is equal to the lower 2 bytes of the sum of all bytes in the entry section
        Note that if the flash bytes are undefined, they are not included in the sum
        """

        return int.to_bytes(sum(self.entry) - (0 if self.flash_bytes else 510) & 0xFFFF, 2, 'little')

    @stringview(header)[:8]
    def magic(self):
        """
        The file magic for the var

        Used to identify if the file is intended for the TI-82, TI-83, or TI-83+ and onward
        Can be one of **TI82**, **TI83**, or **TI83F*
        """
        pass

    @byteview(header)[8:10]
    def extra(self):
        """
        Extra export bytes for the var

        Exact meaning and interpretation of these bytes is not yet determined
        These bytes can often be incorrect without causing issues
        """
        pass

    @byteview(header)[10:11]
    def product_id(self):
        """
        The product ID for the var

        Used to identify the model the var was created on, though has no actual functional ramifications
        Does not constitute a 1-to-1 mapping to distinct models
        """
        pass

    @stringview(header)[11:53]
    def comment(self):
        """
        The comment attached to the var
        """
        pass

    @intview(header)[53:]
    def entry_length(self) -> int:
        """
        The length of the var entry

        Should be 57 less than the total var size
        """

        return len(self.entry)

    @intview(entry)[:2]
    def meta_length(self) -> int:
        """
        The length of the meta section of the var

        Can be 13 (contains flash) or 11 (lacks flash)
        Internally, the meta is always 13 bytes; if the var lacks flash bytes, they are set to 0xFFFF
        """

        return 13 - 2 * (self.meta[-1] == b'\xFF')

    @byteview(entry)[2:15]
    def meta(self):
        """
        The meta section of the var

        Contains the data length, type ID, var name, and flash bytes
        """
        pass

    @intview(meta)[:2]
    def _data_length(self) -> int:
        return len(self.data)

    @byteview(meta)[2:3]
    def type_id(self):
        """
        The type ID of the var

        Specifies how the data section of the var is interpreted
        Must match the type ID of the object type; else, raises a TypeError when loading new data
        If the type ID is not known a priori, use TIVar to construct the object
        """

        return self._type_id

    @stringview(meta)[3:11]
    def name(self, value):
        """
        The name of the var

        Must be 1 to 8 characters in length
        Can include any characters A-Z, 0-9, or Θ
        Cannot start with a digit
        """

        varname = value[:8].upper()
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "[", varname)
        varname = re.sub(r"[^[a-zA-Z0-9]", "", varname)

        if not varname or varname[0].isnumeric():
            warn(f"Var has invalid name: {varname}.")

        return varname

    @intview(meta)[11:12]
    def version(self):
        """
        The version number of this var

        Is undefined for vars without flash bytes
        Internally, is set to 0xFF (read as 255) if undefined
        """
        pass

    @boolview(meta)[12:13]
    def archived(self):
        """
        Whether this var is archived
        A value of 0x80 is truthy; all others are falsy

        Is not present for vars without flash bytes
        Internally, is set to 0xFF (read as False) if undefined
        """
        pass

    @intview(entry)[15:17]
    def data_length(self):
        """
        The length of the data section of the var

        Can be zero
        """

        return self._data_length

    @dataview(entry)[17:]
    def data(self):
        """
        The data section of the var

        See individual var types for how this data is interpreted
        """
        pass

    @property
    def flash_bytes(self):
        return bytes(self.meta[-2:]) if self.meta[-1] != b'\xFF' else b''

    def __init__(self, *, name: str = 'UNNAMED', model: 'TIModel' = None, default_product_id: bool = False):
        super().__init__(74)

        self.name = name
        self.model = model

        self.magic = TI_84P.magic if self.model is None else model.magic
        self.extra = b'\x1a\x0a'

        if not default_product_id and model is not None:
            self.product_id = model.product_id

        self.update()

    def __str__(self) -> str:
        return self.string()

    @property
    def extension(self) -> str:
        try:
            extension = self.extensions[self.model]
            if not extension:
                raise TypeError(f"The {self.model} does not support this var type.")

            return extension

        except KeyError:
            warn(f"Model {self.model} not recognized.")
            return self.extensions[None]

    @staticmethod
    def register(var_type: type['TIVar']):
        TIVar.type_ids[var_type.type_id] = var_type

    def archive(self):
        if self.model is None or self.model.has(TIFeature.FLASH):
            self.archived = True
        else:
            raise TypeError(f"The {self.model} does not support archiving.")

    def bytes(self):
        self.update()

        dump = b''

        dump += self.header
        dump += self.entry[:4]
        dump += self.type_id
        dump += self.meta[3:11]
        dump += self.flash_bytes
        dump += self.entry[15:17]
        dump += self.data
        dump += self.checksum

        return dump

    def load(self, data):
        if isinstance(data, str):
            self.load_string(data)
            return

        try:
            self.load_file(data)
            return

        except AttributeError:
            self.load_bytes(data)

    def load_bytes(self, data: bytes):
        data = io.BytesIO(data)
        self.clear()

        # Read header
        self.extend(data.read(55))

        # Discern model
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

        # Read meta length
        self.extend(data.read(2))

        # Read data length
        self.extend(data_length := data.read(2))

        # Read type ID
        self.extend(type_id := data.read(1))

        # Read varname
        self.extend(data.read(8))

        # Check type ID
        # Needs to come later since the checksum buffer is already allotted
        if self.type_id is None:
            try:
                self.__class__ = TIVar.type_ids[type_id]

            except KeyError:
                raise TypeError(f"Type id 0x{type_id:x} is not recognized.")

        elif type_id != self.type_id:
            raise TypeError("The var type is incorrect. Use a TIVar instance if you don't know the type.")

        # Read flash meta
        match self.meta_length:
            case TIVar.flash_meta_length:
                flash = data.read(2)

                if flash == b'\xFF\xFF':
                    warn(f"The flash bytes are undefined.",
                         BytesWarning)

                elif flash[-1] not in b'\x00\x80':
                    warn(f"The archive flag is set to an unexpected value.",
                         BytesWarning)

            case TIVar.base_meta_length:
                flash = b'\xFF\xFF'

            case _:
                warn(f"The entry meta length has an unexpected value ({self.meta_length}); "
                     f"attempting to read flash bytes anyway.",
                     BytesWarning)
                flash = data.read(2)

        self.extend(flash)

        # Read data
        self.extend(data_length2 := data.read(2))
        if data_length != data_length2:
            warn(f"The var entry data lengths are mismatched ({data_length} vs. {data_length2}).",
                 BytesWarning)

        self.extend(data.read(int.from_bytes(data_length2, 'little')))

        # Read checksum
        self.extend(checksum := data.read(2))
        if checksum != self.checksum:
            warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                 BytesWarning)

    def load_file(self, file: BinaryIO):
        self.load_bytes(file.read())

    def load_string(self, string: str):
        raise NotImplementedError

    def open(self, filename: str):
        if not any(filename.endswith(extension) for extension in self.extensions.values()):
            warn(f"File extension .{filename.split('.')[-1]} not recognized for var type {type(self)}; "
                 f"attempting to read anyway.")

        elif self.model is not None and not filename.endswith(self.extension):
            warn(f"Var type {type(self)} on the {self.model} uses .{self.extension} extension.")

        with open(filename, 'rb') as file:
            self.load_bytes(file.read())

    def save(self, filename: str = None):
        with open(filename or f"{self.name}.{self.extension}", 'wb+') as file:
            file.write(self.bytes())

    def string(self) -> str:
        raise NotImplementedError

    def unarchive(self):
        if self.model is None or self.model.has(TIFeature.FLASH):
            self.archived = False
        else:
            raise TypeError(f"The {self.model} does not support archiving.")

    def update(self):
        updated = self.data_length, self.meta_length, self.type_id, self.entry_length, self.checksum


__all__ = ["TIVar"]
