import copy
import io
import re

from typing import BinaryIO
from warnings import warn

from tivars.models import *
from .data import *


class TIHeaderRaw(Raw):
    __slots__ = "magic", "extra", "product_id", "comment"


class TIHeader:
    def __init__(self, *, magic: str = None, extra: bytes = b'\x1a\x0a', product_id: bytes = None,
                 comment: str = "Created with tivars_lib_py v1.0", model: TIModel = None):
        self.raw = TIHeaderRaw()

        self.magic = magic or model.magic if model is not None else TI_83P.magic
        self.extra = extra
        self.product_id = product_id or model.product_id if model is not None else b'\x00'
        self.comment = comment

    def __bytes__(self) -> bytes:
        return self.bytes()

    def __copy__(self) -> 'TIHeader':
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo) -> 'TIHeader':
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))

        return new

    def __eq__(self, other: 'TIHeader') -> bool:
        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __or__(self, other: list['TIEntry']):
        new = other[0].export(header=self, name=other[0].name, model=other[0].model)

        for entry in other[1:]:
            new.add_entry(entry)

        return new

    def __len__(self) -> int:
        return 53

    @Section(8, String)
    def magic(self) -> str:
        """
        The file magic for the var

        Used to identify if the file is intended for the TI-82, TI-83, or TI-83+ and onward
        Can be one of **TI82**, **TI83**, or **TI83F*
        """
        pass

    @Section(2)
    def extra(self) -> bytes:
        """
        Extra export bytes for the var

        Exact meaning and interpretation of these bytes is not yet determined
        These bytes are set by different export tools and can often be "incorrect" without causing issues
        """
        pass

    @Section(1)
    def product_id(self) -> bytes:
        """
        The product ID for the var

        Used to identify the model the var was created on, though has no actual functional ramifications
        Does not constitute a 1-to-1 mapping to distinct models
        """
        pass

    @Section(42, String)
    def comment(self) -> str:
        """
        The comment attached to the var
        """
        pass

    def bytes(self) -> bytes:
        return self.raw.bytes()

    def derive_model(self) -> TIModel:
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
                    warn(f"The var product ID is not recognized ({self.product_id}).",
                         BytesWarning)
                    model = None

            case _:
                warn(f"The var file magic is not recognized ({self.magic}).",
                     BytesWarning)
                model = None

        return model

    def load_bytes(self, data: bytes):
        data = io.BytesIO(data)

        # Read magic
        self.raw.magic = data.read(8)

        # Read export bytes
        self.raw.extra = data.read(2)

        # Read product ID
        self.raw.product_id = data.read(1)

        # Read comment
        self.raw.comment = data.read(42)

    def load_from_file(self, file: BinaryIO):
        self.load_bytes(file.read(len(self)))

    def open(self, filename: str):
        with open(filename, 'rb') as file:
            self.load_bytes(file.read())


class TIEntryRaw(Raw):
    __slots__ = "meta_length", "_data_length", "type_id", "name", "version", "archived", "_data_length", "data"

    @property
    def data_length(self) -> bytes:
        return int.to_bytes(len(self.data), 2, 'little')

    @property
    def flash_bytes(self) -> bytes:
        return (self.version + self.archived)[:int.from_bytes(self.meta_length, 'little') - TIEntry.base_meta_length]


class TIEntry:
    extensions = {None: "8xg"}
    type_ids = {}

    versions = []

    base_meta_length = 11
    flash_meta_length = 13

    _type_id = None

    def __init__(self, *, model: TIModel = None, name: str = "UNNAMED",
                 version: bytes = b'\x00', archived: bool = False):
        self.raw = TIEntryRaw()

        self.name = name
        self._model = model
        self.raw.type_id = self._type_id

        if model is not None:
            if model.has(TIFeature.FLASH):
                self.version = version
                self.archived = archived
                self.meta_length = TIEntry.flash_meta_length

            else:
                self.meta_length = TIEntry.base_meta_length

        else:
            self.meta_length = TIEntry.flash_meta_length

    def __bytes__(self) -> bytes:
        return self.bytes()

    def __copy__(self) -> 'TIEntry':
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo) -> 'TIEntry':
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))

        return new

    def __eq__(self, other: 'TIEntry') -> bool:
        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __len__(self) -> int:
        return 2 + self.meta_length + 2 + self.data_length

    def __str__(self) -> str:
        return self.string()

    @Section(2, Integer)
    def meta_length(self) -> int:
        """
        The length of the meta section of the entry

        Can be 13 (contains flash) or 11 (lacks flash)
        """

    @property
    def data_length(self) -> int:
        """
        The length of the data section of the entry

        Can be zero
        """

        return len(self.data)

    @Section(1)
    def type_id(self) -> bytes:
        """
        The type ID of the entry

        Used the interpret the contents of the data section of the entry
        """

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

    @Section(1)
    def version(self) -> bytes:
        """
        The version number of the entry

        Is not present for vars without flash bytes
        """
        pass

    @Section(1, Boolean)
    def archived(self) -> bool:
        """
        Whether the entry is archived
        A value of 0x80 is truthy; all others are falsy

        Is not present for vars without flash bytes
        """
        pass

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        See individual entry types for how this data is interpreted
        """
        pass

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

    @property
    def flash_bytes(self) -> bytes:
        return (self.raw.version + self.raw.archived)[:self.meta_length - TIEntry.base_meta_length]

    @property
    def model(self) -> TIModel:
        return self._model

    @staticmethod
    def register(var_type: type['TIEntry']):
        TIEntry.type_ids[var_type._type_id] = var_type

    def archive(self):
        if self.flash_bytes:
            self.archived = True
        else:
            raise TypeError(f"This entry does not support archiving.")

    def bytes(self) -> bytes:
        return self.raw.bytes()

    def export(self, *, header: TIHeader = None, name: str = 'UNNAMED', model: TIModel = None) -> 'TIVar':
        var = TIVar(header=header, name=name or self.name, model=model or self._model)
        var.add_entry(self)
        return var

    def load_bytes(self, data: bytes):
        data = io.BytesIO(data)

        # Read meta length
        self.raw.meta_length = data.read(2)

        # Read data length
        data_length = data.read(2)

        # Read and check type ID
        self.raw.type_id = data.read(1)

        if self._type_id is None:
            try:
                self.__class__ = TIEntry.type_ids[self.raw.type_id]

            except KeyError:
                warn(f"Type id 0x{self.raw.type_id.hex()} is not recognized; entry will not be coerced to a subclass.",
                     BytesWarning)

        elif self.raw.type_id != self._type_id:
            warn(f"The entry type is incorrect (expected {type(self)}, got {TIEntry.type_ids[self.raw.type_id]}). "
                 f"Load the entire var file into a TIVar instance if you don't know the entry type(s).",
                 BytesWarning)

        # Read varname
        self.raw.name = data.read(8)

        # Read flash bytes
        match self.meta_length:
            case TIEntry.flash_meta_length:
                self.raw.version = data.read(1)
                self.raw.archived = data.read(1)

                if self.versions and self.raw.version not in self.versions:
                    warn(f"The version ({self.raw.version.hex()}) is not recognized.",
                         BytesWarning)

                if self.raw.archived not in b'\x00\x80':
                    warn(f"The archive flag ({self.raw.archived.hex()}) is set to an unexpected value.",
                         BytesWarning)

            case TIEntry.base_meta_length:
                self.raw.version = b'\x00'
                self.raw.archived = b'\x00'

            case _:
                warn(f"The entry meta length has an unexpected value ({self.meta_length}); "
                     f"attempting to read flash bytes anyway.",
                     BytesWarning)
                self.raw.version = data.read(1)
                self.raw.archived = data.read(1)

                if self.raw.archived not in b'\x00\x80':
                    warn(f"The archive flag is set to an unexpected value.",
                         BytesWarning)

        # Read data and check length
        data_length2 = data.read(2)
        if data_length != data_length2:
            warn(f"The var entry data lengths are mismatched ({data_length} vs. {data_length2}); "
                 f"using {data_length2} to read the data section.",
                 BytesWarning)

        self.raw.data = data.read(int.from_bytes(data_length2, 'little'))

    def load_from_file(self, file: BinaryIO, *, offset: int = 0):
        # Load header
        header = TIHeader()
        header.load_bytes(file.read(55))

        # Discern model
        model = header.derive_model()

        if self._model is None:
            self._model = model

        elif self._model != model:
            warn(f"The var file comes from a different model (expected {self._model}, got {model}).",
                 UserWarning)

        # Seek to offset
        while offset:
            meta_length = int.from_bytes(file.read(2), 'little')
            data_length = int.from_bytes(file.read(2), 'little')
            file.seek(meta_length + data_length, 1)

            offset -= 1

        self.load_bytes(file.read())

    def load_string(self, string: str):
        raise NotImplementedError

    def open(self, filename: str):
        if not any(filename.endswith(extension) for extension in self.extensions.values()):
            warn(f"File extension .{filename.split('.')[-1]} not recognized for var type {type(self)}; "
                 f"attempting to read anyway.")

        with open(filename, 'rb') as file:
            file.seek(55)
            self.load_bytes(file.read())

    def save(self, filename: str = None, *, header: TIHeader = TIHeader()):
        self.export(header=header).save(filename)

    def string(self) -> str:
        raise NotImplementedError

    def unarchive(self):
        if self.flash_bytes:
            self.archived = False
        else:
            raise TypeError(f"This entry does not support archiving.")


class TIVar:
    def __init__(self, *, header: TIHeader = None, name: str = 'UNNAMED', model: TIModel = None):
        super().__init__()

        self.header = header or TIHeader(model=model)
        self.entries = []

        self.name = name
        self._model = model

    def __bytes__(self):
        return self.bytes()

    def __copy__(self) -> 'TIVar':
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo) -> 'TIVar':
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))

        return new

    def __eq__(self, other: 'TIVar'):
        try:
            eq = self.__class__ == other.__class__ and len(self.entries) == len(other.entries)
            return eq and all(entry == other_entry for entry, other_entry in zip(self.entries, other.entries))

        except AttributeError:
            return False

    def __len__(self):
        return len(self.header) + self.entry_length + 2

    @property
    def entry_length(self) -> int:
        """
        The total length of the var entries

        Should be 57 less than the total var size
        """

        return sum(len(entry) for entry in self.entries)

    @property
    def checksum(self):
        """
        The checksum for the var

        This is equal to the lower 2 bytes of the sum of all bytes in the entries
        """

        return int.to_bytes(sum(sum(entry.bytes()) for entry in self.entries) & 0xFFFF, 2, 'little')

    @property
    def extension(self) -> str:
        try:
            extension = self.entries[0].extensions[self._model]
            if not extension:
                raise TypeError(f"The {self._model} does not support this var type.")

        except KeyError:
            warn(f"Model {self._model} not recognized.")
            extension = self.entries[0].extensions[None]

        if len(self.entries) == 1:
            return extension

        else:
            return "8xg"

    @property
    def model(self) -> TIModel:
        return self.model

    def add_entry(self, entry: TIEntry = None):
        self.entries.append(entry or TIEntry(model=self._model))

    def bytes(self):
        dump = self.header.bytes()
        dump += int.to_bytes(self.entry_length, 2, 'little')

        for entry in self.entries:
            dump += entry.bytes()

        dump += self.checksum
        return dump

    def load_bytes(self, data: bytes):
        data = io.BytesIO(data)

        # Read header
        self.header.load_bytes(data.read(53))
        entry_length = int.from_bytes(data.read(2), 'little')

        # Read entries
        while entry_length:
            self.add_entry()

            meta_length = int.from_bytes(data.read(2), 'little')
            data_length = int.from_bytes(data.read(2), 'little')

            self.entries[-1].load_bytes(int.to_bytes(meta_length, 2, 'little') +
                                        int.to_bytes(data_length, 2, 'little') +
                                        data.read(meta_length + data_length))

            entry_length -= 2 + meta_length + 2 + data_length

        # Read checksum
        checksum = data.read(2)

        # Discern model
        model = self.header.derive_model()

        if self._model is None:
            self._model = model

        elif self._model != model:
            warn(f"The var file comes from a different model (expected {self._model}, got {model}).")

        # Check² sum
        if checksum != self.checksum:
            warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                 BytesWarning)

    def load_var_file(self, file: BinaryIO):
        self.load_bytes(file.read())

    def open(self, filename: str):
        with open(filename, 'rb') as file:
            self.load_bytes(file.read())

    def save(self, filename: str = None):
        with open(filename or f"{self.name}.{self.extension}", 'wb+') as file:
            file.write(self.bytes())


__all__ = ["TIHeader", "TIEntry", "TIVar"]
