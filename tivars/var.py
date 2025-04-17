"""
The fundamental var components
"""


import re

from collections.abc import Iterator
from io import BytesIO
from sys import version_info
from typing import BinaryIO
from warnings import catch_warnings, simplefilter, warn

from .data import *
from .file import *
from .models import *
from .tokenizer import Name


# Use Self type if possible
match version_info[:2]:
    case 3, 10:
        Self = 'TIEntry'

    case _:
        from typing import Self


class TIHeader:
    """
    Parser for var file headers

    All var files require a header which includes a number of magic bytes, data lengths, and a customizable comment.
    """

    magics = [model.magic for model in TIModel.MODELS]

    length = 53

    class Raw:
        """
        Raw bytes container for `TIHeader`

        Any class with a distinct byte format requires its own ``Raw`` class to contain its data sections.
        Each data section must have a corresponding slot in ``Raw`` in order to use `Converter` classes.

        The ``Raw`` class must also contain a ``bytes()`` method specifying the order of the data sections.
        Additional methods can also be included, but should be callable from the outer class.
        """

        __slots__ = "magic", "extra", "product_id", "comment"

        def bytes(self) -> bytes:
            """
            :return: The bytes contained in this header
            """

            return self.magic + self.extra + self.product_id + self.comment

    def __init__(self, model: TIModel = TI_84PCE, *,
                 magic: str = None, extra: bytes = b'\x1a\x0a', product_id: int = None,
                 comment: str = "Created with tivars_lib_py v0.9.2",
                 data: bytes = None):
        """
        Creates an empty header which targets a specified model

        :param model: A minimum `TIModel` to target (defaults to ``TI_84PCE``)
        :param magic: File magic at the start of the header (default to the model's magic)
        :param extra: Extra export bytes for the header (defaults to ``$1a0a``)
        :param product_id: The targeted model's product ID (defaults to ``$00``)
        :param comment: A comment to include in the header (defaults to a simple lib message)
        :param data: This header's data (defaults to empty)
        """

        self.raw = self.Raw()

        self.magic = magic or model.magic
        self.extra = extra
        self.product_id = product_id if product_id is not None else model.product_id
        self.comment = comment

        matches = {m for m in TIModel.MODELS if m.magic == self.magic}

        self._supports = {m for m in TIModel.MODELS if m >= min(matches)}
        if not self._supports:
            warn(f"File magic '{self.magic}' not recognized.",
                 BytesWarning)

        self._targets = {m for m in self._supports if self.product_id == 0x00 or m.product_id == self.product_id}
        if self.product_id != 0x00 and not self._targets:
            warn(f"Product ID {self.product_id:02x} not recognized.",
                 BytesWarning)

        if data:
            self.load_bytes(data)

    def __bytes__(self) -> bytes:
        """
        :return: The bytes contained in this header
        """

        return self.bytes()

    def __copy__(self) -> 'TIHeader':
        """
        :return: A copy of this header
        """

        new = TIHeader()
        new.load_bytes(self.bytes())
        return new

    def __eq__(self, other: 'TIHeader') -> bool:
        """
        Determines if two headers have the same bytes

        :param other: The header to check against
        :return: Whether this header is equal to ``other``
        """

        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __or__(self, other: list['TIEntry']) -> 'TIVarFile':
        """
        Constructs a var by concatenating this header with a list of entries

        :param other: A list of entries to place into the var
        :return: A var with this header and ``other`` as its entries
        """

        new = other[0].export(header=self, name=other[0].name)

        for entry in other[1:]:
            new.add_entry(entry)

        return new

    def __len__(self) -> int:
        """
        :return: The total length of this header's bytes
        """

        return self.length

    @Section(8, String)
    def magic(self) -> str:
        """
        The file magic for the var
        """

    @Section(2)
    def extra(self) -> bytes:
        """
        Extra export bytes for the var

        The exact meaning and interpretation of these bytes is not yet determined.
        These bytes are set by different export tools and can often be "incorrect" without causing issues.
        """

    @Section(1, Bits[:])
    def product_id(self) -> int:
        """
        The product ID for the var

        While used to identify the model the var was created on, it has no actual functional ramifications.
        Furthermore, it does not constitute a 1-to-1 mapping to distinct models.
        """

    @Section(42, String)
    def comment(self) -> str:
        """
        The comment attached to the var
        """

    def supported_by(self, model: TIModel = TI_84PCE) -> bool:
        """
        Determines whether this header supports a given model

        See `TIHeader.targets` to check models this header explicitly targets.

        :param model: The model to check support for
        :return: Whether ``model`` supports this header
        """

        return model.magic == self.magic

    def targets(self, model: TIModel = TI_84PCE) -> bool:
        """
        Determines whether this header targets a given model

        The header contains no reference to a model to target, which permits sharing across models where possible.
        This method derives a set of valid models from the header's file magic and product ID.

        See `TIHeader.supported_by` to check models this header _can_ be sent be to.

        :param model: The model to check as a target
        :return: Whether ``model`` is targeted by this header
        """

        return self.supported_by(model) and self.product_id in (0x00, model.product_id)

    def load_bytes(self, data: bytes | BytesIO):
        """
        Loads a byte string or bytestream into the header

        :param data: The source bytes
        """

        if hasattr(data, "read"):
            data = BytesIO(data.read())

        data = BytesIO(data.ljust(len(self), b'\x00'))

        # Read magic
        self.raw.magic = data.read(8)

        # Read export bytes
        self.raw.extra = data.read(2)

        # Read product ID
        self.raw.product_id = data.read(1)

        # Read comment
        self.raw.comment = data.read(42)

    def bytes(self) -> bytes:
        """
        :return: The bytes contained in this header
        """

        return self.raw.bytes()

    def load_from_file(self, file: BinaryIO):
        """
        Loads this header from a file given a file pointer

        :param file: A binary file to read from
        """

        self.load_bytes(file.read(len(self)))

    @classmethod
    def open(cls, filename: str) -> 'TIHeader':
        """
        Creates a new header from a file given a filename

        :param filename: A filename to open
        :return: The header stored in the file
        """

        with open(filename, 'rb') as file:
            return cls(data=file.read())


class TIEntry(Dock, Converter):
    """
    Base class for all var entries

    A var file is made of one or more entries, each of which contain the data of the familiar var types.

    **Even though most var files have just one entry, an entry does NOT constitute a complete var file.**
    **All var files require an attached header and other metadata.**

    **Use** `TIEntry.export` **to create a new** `TIVarFile` **containing the entry, with an optional custom header.**
    **Use** `TIEntry.save` **to export and save the entry in a var file in the current directory.**
    """

    _T = 'TIEntry'

    flash_only = False
    """
    Whether this entry only supports flash chips
    """

    versions = [0x00]
    """
    The possible versions of this entry
    """

    extension = "8xg"
    """
    The base file extension used for this entry
    """

    base_meta_length = 11
    flash_meta_length = 13

    min_calc_data_length = 0
    """
    The minimum length of this entry's data
    
    If an entry's data is fixed in size, this value is necessarily the length of the data
    """

    leading_name_byte = b''
    """
    Byte that always begins the name of this entry
    """

    leading_data_bytes = b''
    """
    Bytes that always begin this entry's data
    """

    _type_id = None
    _type_ids = {}

    class Raw:
        """
        Raw bytes container for `TIEntry`

        Any class with a distinct byte format requires its own ``Raw`` class to contain its data sections.
        Each data section must have a corresponding slot in ``Raw`` in order to use `Converter` classes.

        The ``Raw`` class must also contain a ``bytes()`` method specifying the order of the data sections.
        Additional methods can also be included, but should be callable from the outer class.

        Most entry types do not require a new ``Raw`` class since only the entry's data changes between types.
        """

        __slots__ = "meta_length", "type_id", "name", "version", "archived", "calc_data"

        @property
        def calc_data_length(self) -> bytes:
            """
            :return: The length of this entry's data portion
            """

            return int.to_bytes(len(self.calc_data), 2, 'little')

        @property
        def flash_bytes(self) -> bytes:
            """
            :return: The flash bytes of this entry if they exist
            """

            return (self.version + self.archived)[
                   :int.from_bytes(self.meta_length, 'little') - TIEntry.base_meta_length]

        @property
        def meta(self) -> bytes:
            """
            :return: The meta section of this entry
            """

            return self.calc_data_length + self.type_id + self.name + self.flash_bytes

        def bytes(self) -> bytes:
            """
            :return: The bytes contained in this entry
            """

            return self.meta_length + self.meta + self.calc_data_length + self.calc_data

    def __init__(self, init=None, *,
                 name: str = "UNNAMED",
                 version: int = None, archived: bool = None,
                 data: bytes = None):
        """
        Creates an empty entry with specified meta and data values

        :param init: Values to initialize the entry's data (defaults to ``None``)
        :param name: The name of the entry (defaults to a valid default name)
        :param version: The entry's version (defaults to ``None``)
        :param archived: Whether the entry is archived (defaults to entry's default state on-calc)
        :param data: The entry's data (defaults to empty)
        """

        self.raw = self.Raw()

        self.meta_length = TIEntry.flash_meta_length
        self.type_id = self._type_id if self._type_id is not None else 0xFF
        self.name = name
        self.archived = archived if archived is not None else False
        self.version = version or 0x00

        self.clear()
        if data:
            self.data = bytearray(data)
            self.coerce()

        elif init is not None:
            if hasattr(init, "bytes"):
                self.load_bytes(init.bytes())

            else:
                self.load(init)

        if version is None:
            self.version = self.get_version()

    def __bool__(self) -> bool:
        """
        :return: Whether this entry's data is empty
        """

        return not self.is_empty

    def __bytes__(self) -> bytes:
        """
        :return: The bytes contained in this entry
        """

        return self.bytes()

    def __copy__(self) -> Self:
        """
        :return: A copy of this entry
        """

        new = self.__class__()
        new.load_bytes(self.bytes())
        return new

    def __eq__(self, other: 'TIEntry') -> bool:
        """
        Determines if two entries are the same type and have the same bytes

        :param other: The entry to check against
        :return: Whether this entry is equal to ``other``
        """

        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __format__(self, format_spec: str) -> str:
        """
        Formats this entry for string representations

        :param format_spec: The format parameters
        :return: A string representation of this entry
        """

        if match := re.fullmatch(r"(?P<width>[+-]?\d+)?(?P<case>[xX])(?P<sep>\D)?", format_spec):
            match match["sep"], match["width"]:
                case None, None:
                    string = self.calc_data.hex()

                case sep, None:
                    string = self.calc_data.hex(sep)

                case None, width:
                    string = self.calc_data.hex(" ", int(width))

                case sep, width:
                    string = self.calc_data.hex(sep, int(width))

            return string.lower() if match["case"] == "x" else string.upper()

        elif not format_spec:
            return super().__str__()

        else:
            raise TypeError(f"unsupported format string passed to {type(self)}.__format__")

    def __init_subclass__(cls, /, register=False, override=None, **kwargs):
        super().__init_subclass__(**kwargs)

        if register:
            TIEntry.register(cls, override)

    def __iter__(self) -> Iterator:
        """
        :return: If this entry is a container or collection, an iterator over its elements
        """

        raise NotImplementedError

    def __len__(self) -> int:
        """
        :return: The total length of this entry's bytes
        """

        return 2 + self.meta_length + 2 + self.calc_data_length

    def __str__(self) -> str:
        """
        :return: A string representation of this entry
        """

        return self.string()

    @Section(2, Integer)
    def meta_length(self, value) -> int:
        """
        The length of the meta section of the entry

        The possible meta lengths are 11 (without flash) or 13 (with flash).
        """

        if value == TIEntry.base_meta_length:
            if self.raw.meta_length == TIEntry.flash_meta_length.to_bytes(2, 'little'):
                warn(f"Meta data (0x{self.flash_bytes.hex()}) will be lost.",
                     UserWarning)

            if self.flash_only:
                warn(f"{type(self)} vars are not compatible with flashless chips.",
                     UserWarning)

        return value

    @property
    def calc_data_length(self) -> int:
        """
        The length of the data section of the entry
        """

        return len(self.calc_data)

    @Section(1, Bits[:], class_attr=True)
    def type_id(self) -> int:
        """
        The type ID of the entry

        The type determines how the contents of the data section of the entry are interpreted.
        """

    @Section(8, Name)
    def name(self) -> str:
        """
        The name of the entry

        Interpretation as text depends on the entry type; see individual types for details.
        """

    @Section(1, Bits[:])
    def version(self, value) -> int:
        """
        The version number of the entry

        The version is used to determine model compatibility where necessary.
        Only flash files support this section, and is thus not present if `meta_length` < 13.
        """

        if self.meta_length == TIEntry.base_meta_length:
            warn(f"Flashless vars do not maintain version information.",
                 UserWarning)

        return value

    @Section(1, Boolean)
    def archived(self, value) -> bool:
        """
        Whether the entry is archived

        Only flash files support this section, and is thus not present if `meta_length` < 13.
        """

        if self.meta_length == TIEntry.base_meta_length:
            warn(f"Flashless vars cannot be archived or unarchived.",
                 UserWarning)

        return value

    @Section()
    def calc_data(self) -> bytes:
        """
        The data section of the entry which is loaded on-calc
        """

    @View(calc_data, Data)[:]
    def data(self) -> bytes:
        """
        The entry's user data
        """

    @classmethod
    def get(cls, data: bytes, **kwargs) -> _T:
        """
        Converts ``bytes`` -> `TIEntry`

        :param data: The raw bytes to convert
        :return: A `TIEntry` instance with data equal to ``data``
        """

        return cls(data=data)

    @classmethod
    def set(cls, value: _T, **kwargs) -> bytes:
        """
        Converts `TIEntry` -> ``bytes``

        :param value: The value to convert
        :return: The data of ``value``
        """

        return value.calc_data

    @property
    def flash_bytes(self) -> bytes:
        """
        :return: The flash bytes of this entry if they exist
        """

        return (self.raw.version + self.raw.archived)[:self.meta_length - TIEntry.base_meta_length]

    @property
    def for_flash(self) -> bool:
        """
        :return: Whether this entry supports flash chips
        """

        return self.meta_length >= TIEntry.flash_meta_length

    @property
    def is_empty(self) -> bool:
        """
        :return: Whether this entry's data is empty
        """

        return self.calc_data_length == 0

    @property
    def meta(self) -> bytes:
        """
        :return: The meta section of this entry
        """

        return self.raw.meta

    @classmethod
    def get_type(cls, type_id: int) -> type['TIEntry'] | None:
        """
        Gets the subclass corresponding to a type ID if one is registered

        :param type_id: The type ID to search by
        :return: A subclass of `TIEntry` with corresponding type ID or ``None``
        """

        return cls._type_ids.get(type_id, None)

    @staticmethod
    def next_entry_length(stream: BinaryIO) -> int:
        """
        Helper function to determine the length of the next entry in a bytestream

        :param stream: A bytestream
        :return: The length of the next entry in the bytestream
        """

        meta_length = int.from_bytes(stream.read(2), 'little')
        data_length = int.from_bytes(stream.read(2), 'little')
        stream.seek(-4, 1)

        if meta_length not in (TIEntry.base_meta_length, TIEntry.flash_meta_length):
            warn(f"Got unexpected meta length ({meta_length}) from bytestream.",
                 BytesWarning)

        return 2 + meta_length + 2 + data_length

    @classmethod
    def register(cls, var_type: type['TIEntry'], override: int = None):
        """
        Registers a subtype with this class for coercion

        :param var_type: The `TIEntry` subtype to register
        :param override: A type ID to use for registry that differs from that of the var type
        """

        cls._type_ids[var_type._type_id if override is None else override] = var_type

    def archive(self):
        """
        Archives this entry
        """

        self.archived = True

        if not self.for_flash:
            warn(f"This entry's meta length is too short ({self.meta_length}), and thus does not support archiving.",
                 UserWarning)

    def clear(self):
        """
        Clears this entry's data
        """

        self.raw.calc_data = bytearray(self.leading_data_bytes)
        self.raw.calc_data.extend(bytearray(self.min_calc_data_length - self.calc_data_length))

    @datamethod
    @classmethod
    def get_min_os(cls, data: bytes) -> OsVersion:
        """
        Determines the minimum OS that supports this entry's data

        :param data: The data to find the minimum support for (defaults to this entry's data)
        :return: The minimum ``OsVersion`` this entry supports
        """

        return OsVersions.INITIAL

    @datamethod
    @classmethod
    def get_version(cls, data: bytes) -> int:
        """
        Determines the version byte corresponding to given data for this entry type

        Entries which could contain non-backwards compatible data are assigned a version byte.
        If an entry's version exceeds the "version" of a calculator, transfer to the calculator will fail.

        :param data: The data to find the version of (defaults to this entry's data)
        :return: The version byte for ``data``
        """

        return cls.versions[0]

    def supported_by(self, model: TIModel) -> bool:
        """
        Determines whether a given model supports this entry

        :param model: The model to check support for
        :return: Whether ``model`` supports this entry
        """

        return self.get_min_os() < model.OS("latest")

    def unarchive(self):
        """
        Unarchives this entry
        """

        self.archived = False

        if not self.for_flash:
            warn(f"This entry's meta length is too short ({self.meta_length}), and thus does not support archiving.",
                 UserWarning)

    @Loader[bytes, bytearray, BytesIO]
    def load_bytes(self, data: bytes):
        """
        Loads a byte string or bytestream into this entry

        :param data: The bytes to load
        """

        if hasattr(data, "read"):
            data = data.read()

        data = BytesIO(data.ljust(TIEntry.flash_meta_length + 4, b'\x00'))

        # Read meta length
        self.raw.meta_length = data.read(2)

        # Read data length
        data_length = data.read(2)

        # Read and check type ID
        self.raw.type_id = data.read(1)

        if self._type_id is not None and self.type_id != self._type_id:
            if subclass := TIEntry.get_type(self.type_id):
                if not issubclass(subclass, self.__class__):
                    warn(f"The entry type is incorrect (expected {type(self)}, got {subclass}).",
                         BytesWarning)

            else:
                warn(f"The entry type is incorrect (expected {type(self)}, got an unknown type). "
                     f"Load the entry into a base TIEntry instance if you don't know the entry type.",
                     BytesWarning)

        # Read varname
        self.raw.name = data.read(8)

        # Read flash bytes
        match self.meta_length:
            case TIEntry.flash_meta_length:
                self.raw.version = data.read(1)
                self.raw.archived = data.read(1)

            case TIEntry.base_meta_length:
                self.raw.version = b'\x00'
                self.raw.archived = b'\x00'

            case _:
                warn(f"The entry meta length has an unexpected value ({self.meta_length}); "
                     f"attempting to read flash bytes anyway.",
                     BytesWarning)

                self.raw.version = data.read(1)
                self.raw.archived = data.read(1)

        if self.meta_length == TIEntry.flash_meta_length and self.raw.version + self.raw.archived == data_length:
            warn(f"The entry meta length is {self.meta_length}, but the flash data is likely missing; "
                 f"the meta section will be corrected to be flashless.")

            self.meta_length = TIEntry.base_meta_length
            self.raw.version = b'\x00'
            self.raw.archived = b'\x00'

        else:
            if self.raw.archived not in b'\x00\x80':
                warn(f"The archive flag (0x{self.raw.archived.hex()}) is set to an unexpected value.",
                     BytesWarning)

            # Check length
            data_length2 = data.read(2)
            if data_length != data_length2:
                warn(f"The var entry data lengths are mismatched ({data_length} vs. {data_length2}); "
                     f"using {data_length} to read the data section.",
                     BytesWarning)

        # Read data
        self.raw.calc_data = bytearray(data.read(length := int.from_bytes(data_length, 'little')))

        if len(self.calc_data) != length:
            warn(f"The data section length is incorrect (expected {length}, got {len(self.calc_data)}).",
                 BytesWarning)

        self.coerce()

        if self.versions != [0x00] and self.version not in self.versions:
            warn(f"The version (0x{self.version:02x}) is not recognized.",
                 BytesWarning)

        if self.meta_length == TIEntry.base_meta_length and self.flash_only:
            warn(f"{type(self)} vars are not compatible with flashless chips.",
                 BytesWarning)

    def bytes(self) -> bytes:
        """
        The bytes contained in this entry, without any var file header or metadata.

        **These bytes do NOT constitute a complete var file. Use** `.export` **and** `.save` **to save a var file.**

        :return: The bytes contained in this entry
        """

        return self.raw.bytes()

    def load_data_section(self, data: BytesIO):
        """
        Loads the data of this entry from a bytestream

        :param data: The source bytes
        """

        self.raw.calc_data = bytearray(data.read(type(self).calc_data.length))

    @Loader[dict]
    def load_dict(self, dct: dict):
        """
        Loads this entry from a JSON dictionary representation

        :param dct: The dict to load
        """

        raise NotImplementedError

    def dict(self) -> str:
        """
        :return: A JSON dictionary representation of this entry
        """

        raise NotImplementedError

    @Loader[BinaryIO]
    def load_from_file(self, file: BinaryIO, *, offset: int = 0):
        """
        Loads this entry from a file given a file pointer and offset

        :param file: A binary file to read from
        :param offset: The offset of the entry to read
        """

        # Skip header
        header = TIHeader()
        header.load_from_file(file)
        file.seek(2, 1)

        # Seek to offset
        while offset:
            file.seek(self.next_entry_length(file), 1)
            offset -= 1

        self.load_bytes(file.read(self.next_entry_length(file)))
        file.seek(2, 1)

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this entry from a string representation

        If there is no dedicated handler for an entry type, all subclasses of the type will be considered.

        :param string: The string to load
        """

        with catch_warnings():
            simplefilter("ignore")

            for entry_type in self._type_ids.values():
                if issubclass(entry_type, self.__class__):
                    try:
                        # Try out each possible string format
                        self.load_bytes(entry_type(string).bytes())
                        return

                    except Exception:
                        continue

        raise ValueError(f"could not parse '{string}' as entry type")

    def string(self) -> str:
        """
        :return: A string representation of this entry
        """

        return format(self, "")

    @classmethod
    def open(cls, filename: str) -> Self:
        """
        Creates a new entry from a file given a filename

        :param filename: A filename to open
        :return: The (first) entry stored in the file
        """

        if cls._type_id is not None and not re.search(rf"\.{cls.extension.replace('x', '.')}$", filename.lower()):
            warn(f"File extension .{filename.split('.')[-1]} not recognized for var type {cls}; "
                 f"attempting to read anyway.",
                 UserWarning)

        with open(filename, 'rb') as file:
            # Use header for sanity check
            header = TIHeader()
            header.load_from_file(file)

            data_length = int.from_bytes(file.read(2), 'little')
            entry_length = cls.next_entry_length(file)

            entry = cls()
            entry.load_bytes(file.read(entry_length))

            if (remaining := file.read())[2:]:
                if remaining.startswith((TIEntry.base_meta_length.to_bytes(2, 'little'),
                                         TIEntry.flash_meta_length.to_bytes(2, 'little'))):
                    warn("The selected var file contains multiple entries; only the first will be loaded. "
                         "Use load_from_file to select a particular entry, or load the entire file into a TIVarFile object.",
                         UserWarning)

                else:
                    warn(f"The selected var file contains unexpected additional data: {remaining}.",
                         BytesWarning)

            elif data_length != entry_length:
                warn(f"The entry length is incorrect (expected {entry_length}, got {data_length}).",
                     BytesWarning)

        return entry

    def save(self, filename: str = None, *, header: TIHeader = None, model: TIModel = TI_84PCE):
        """
        Saves this entry as a var file in the current directory given a filename and optional header and targeted model

        :param filename: A filename to save to (defaults to the var's name and extension)
        :param header: A `TIHeader` to attach (defaults to an empty header)
        :param model: A `TIModel` to target (defaults to ``None``)
        """

        self.export(header=header).save(filename, model=model)

    def export(self, *, name: str = None, header: TIHeader = None) -> 'TIVarFile':
        """
        Exports this entry to a `TIVarFile` with a specified name and header

        :param name: The name of the var (defaults to this entry's name)
        :param header: A `TIHeader` to attach (defaults to an empty header)
        """

        var = TIVarFile(header=header, name=name or self.name)
        var.add_entry(self)
        return var

    def coerce(self):
        """
        Coerces this entry to a subclass if possible using the entry's type ID

        Valid types must be registered to be considered for coercion.
        """

        if self._type_id is None:
            if subclass := self.get_type(self.type_id):
                self.__class__ = subclass
                self.coerce()

            elif self.type_id != 0xFF:
                warn(f"Type ID 0x{self.type_id:02x} is not recognized; no coercion will occur.",
                     BytesWarning)

            else:
                warn("Type ID is 0xFF; no coercion will occur.",
                     UserWarning)


class TIVarFile(TIFile, register=True):
    """
    Container for var files

    A var file is composed of a header and any number of entries (though most have only one).
    """

    magics = TIHeader.magics

    def __init__(self, *, name: str = "UNNAMED", header: TIHeader = None, data: bytes = None):
        """
        Creates an empty var with a specified name, header, and targeted model

        :param name: The name of the var (defaults to ``UNNAMED``)
        :param header: A `TIHeader` to attach (defaults to an empty header)
        :param data: The var's data (defaults to empty)
        """

        self.header = header or TIHeader()
        self.entries = []

        super().__init__(name=name, data=data)

    def __bool__(self) -> bool:
        """
        :return: Whether this var contains no entries
        """

        return not self.is_empty

    @property
    def entry_length(self) -> int:
        """
        The total length of the var entries

        This should always be 57 less than the total var size.
        """

        return sum(len(entry) for entry in self.entries)

    @property
    def checksum(self) -> bytes:
        """
        The checksum for the var

        This is equal to the lower 2 bytes of the sum of all bytes in the entries.
        """

        return int.to_bytes(sum(sum(entry.bytes()) for entry in self.entries) & 0xFFFF, 2, 'little')

    @property
    def is_empty(self) -> bool:
        """
        :return: Whether this var contains no entries
        """

        return len(self.entries) == 0

    def add_entry(self, entry: TIEntry = None):
        """
        Adds an entry to this var

        :param entry: A `TIEntry` to add (defaults to an empty entry)
        """

        entry = entry or TIEntry()

        if not self.is_empty:
            if entry.meta_length != self.entries[0].meta_length:
                warn(f"The new entry has a conflicting meta length "
                     f"(expected {self.entries[0].meta_length}, got {entry.meta_length}).",
                     UserWarning)

        self.entries.append(entry)

    def clear(self):
        """
        Removes all entries from this var
        """

        self.entries = []

    def get_extension(self, model: TIModel = TI_84PCE) -> str:
        if len(self.entries) != 1:
            if self.is_empty:
                warn("This var is empty.",
                     UserWarning)

            extension = "8xg"

        else:
            extension = self.entries[0].extension

        if model == TI_82:
            return extension.replace("x", "2")

        elif model == TI_83:
            return extension.replace("x", "3")

        else:
            return extension

    def supported_by(self, model: TIModel) -> bool:
        return all(item.supported_by(model) for item in [self.header, *self.entries])

    def targets(self, model: TIModel) -> bool:
        return self.header.targets(model)

    @Loader[bytes, bytearray, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        if hasattr(data, "read"):
            data = BytesIO(data.read())

        else:
            data = BytesIO(data)

        # Read header
        self.header = TIHeader(data=data.read(TIHeader.length))
        entry_length = int.from_bytes(data.read(2), 'little')

        # Read entries
        self.clear()
        while entry_length > 0:
            self.add_entry()

            length = TIEntry.next_entry_length(data)
            self.entries[-1].load_bytes(entry_data := data.read(length))

            if len(entry_data) != length:
                warn(f"The data length of entry #{len(self.entries) - 1} ({type(self.entries[-1])}) is incorrect "
                     f"(expected {length}, got {len(entry_data)}).",
                     BytesWarning)

            entry_length -= length

        if entry_length < 0:
            warn(f"The total length of entries is incorrect (expected {self.entry_length + entry_length}, "
                 f"got {self.entry_length}).",
                 BytesWarning)

        # Read checksum
        checksum = data.read(2)

        # Check² sum
        if checksum != self.checksum:
            warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                 BytesWarning)

        if remaining := data.read():
            warn(f"The selected var file contains unexpected additional data: {remaining}.",
                 BytesWarning)

    def bytes(self) -> bytes:
        dump = self.header.bytes()
        dump += int.to_bytes(self.entry_length, 2, 'little')

        for entry in self.entries:
            dump += entry.bytes()

        dump += self.checksum
        return dump

    @classmethod
    def open(cls, filename: str) -> 'TIVarFile':
        with open(filename, 'rb') as file:
            return cls(data=file.read())

    def save(self, filename: str = None, model: TIModel = TI_84PCE):
        for index, entry in enumerate(self.entries):
            if entry.get_min_os() > model.OS("latest"):
                warn(f"Entry #{index + 1} is not supported by {model}.",
                     UserWarning)

        super().save(filename, model)


class SizedEntry(TIEntry):
    """
    Base class for all sized entries

    A sized entry is an entry with variable-length data, where the length of the data is stored in the first two bytes.
    This length is two less than the length stored in the ``data_length`` section(s).
    """

    min_calc_data_length = 2

    @Section()
    def calc_data(self) -> bytes:
        pass

    @View(calc_data, Integer)[0:2]
    def length(self) -> int:
        """
        The length of this entry's user data section
        """

    @View(calc_data, SizedData)[2:]
    def data(self) -> bytes:
        pass

    def clear(self):
        self.raw.calc_data = bytearray([0, 0, *self.leading_data_bytes])
        self.raw.calc_data.extend(bytearray(self.min_calc_data_length - self.calc_data_length))
        self.length = len(self.leading_data_bytes) + len(self.data)

    @Loader[bytes, bytearray, BytesIO]
    def load_bytes(self, data: bytes):
        super().load_bytes(data)

        if self.length != (data_length := len(self.leading_data_bytes) + len(self.data)):
            warn(f"The entry has an unexpected data length (expected {self.length}, got {data_length}).",
                 BytesWarning)

    def load_data_section(self, data: BytesIO):
        data_length = int.from_bytes(length_bytes := data.read(2), 'little')
        self.raw.calc_data = bytearray(length_bytes + data.read(data_length))


__all__ = ["TIHeader", "TIEntry", "TIVarFile", "SizedEntry"]
