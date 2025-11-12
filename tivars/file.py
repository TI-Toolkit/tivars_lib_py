"""
The fundamental file components
"""


from io import BytesIO
from pathlib import Path
from sys import version_info
from typing import BinaryIO, TypeAlias
from warnings import catch_warnings, simplefilter, warn

from .data import *
from .models import *
from .util import *


# Use Self type if possible
match version_info[:2]:
    case 3, 10:
        Self: TypeAlias = 'TIComponent'

    case _:
        from typing import Self


class TIComponent(Dock, Converter):
    """
    Base class for data components of TI files

    The subclasses of `TIComponent` are `TIEntry` (for var files) and `TIFlashHeader` (for flash files).
    Note that `TIHeader` is **not** a `TIComponent` due to not having proper attached data.
    """

    _type_id: int = None
    _type_ids: dict[int, type[Self]] = {}

    class Raw:
        """
        Raw bytes container for this component

        Any class with a distinct byte format requires its own `Raw` class to contain its data sections.
        Each data section must have a corresponding slot in `Raw` in order to use `Converter` classes.

        The `Raw` class must also contain a `bytes()` method specifying the order and visibility of the data sections.
        Additional methods can also be included, but should be callable from the outer class.
        """

        __slots__ = "calc_data",

        def bytes(self) -> bytes:
            """
            :return: The bytes contained in this components
            """

            raise NotImplementedError

    def __init__(self, init=None, *, data: bytes = None):
        """
        Creates an empty component with specified data

        :param init: Values to initialize the component's data (defaults to ``None``)
        :param data: The component's data (defaults to empty)
        """

        self.clear()
        if data:
            self.data = bytearray(data)
            self.coerce()

        elif init is not None:
            if hasattr(init, "bytes"):
                self.load_bytes(init.bytes())

            else:
                self.load(init)

    def __bool__(self) -> bool:
        """
        :return: Whether this component's data is empty
        """

        return not self.is_empty

    def __bytes__(self) -> bytes:
        """
        :return: The bytes contained in this component
        """

        return self.bytes()

    def __copy__(self) -> Self:
        """
        :return: A copy of this component
        """

        new = self.__class__()
        new.load_bytes(self.bytes())
        return new

    def __eq__(self, other) -> bool:
        """
        Determines if two components are the same type and have the same bytes

        :param other: The component to check against
        :return: Whether this component is equal to ``other``
        """

        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __format__(self, format_spec: str) -> str:
        return hex_format(self.calc_data, format_spec)

    def __len__(self) -> int:
        """
        :return: The total length of this component's bytes
        """

        raise NotImplementedError

    def __str__(self) -> str:
        """
        :return: A string representation of this component
        """

        return self.string()

    @Section()
    def type_id(self) -> int:
        """
        The (first) type ID of the component
        """

        raise NotImplementedError

    @Section()
    def calc_data(self) -> bytearray:
        """
        The data section of the component which is loaded on-calc
        """

    @View(calc_data, Data)[:]
    def data(self) -> bytes:
        """
        The component's user data
        """

    @classmethod
    def get(cls, data: bytes, **kwargs) -> Self:
        """
        Converts ``bytes`` -> `TIComponent`

        :param data: The raw bytes to convert
        :return: A `TIComponent` instance with data equal to ``data``
        """

        return cls(data=data)

    @classmethod
    def set(cls, value: Self, **kwargs) -> bytes:
        """
        Converts `TIComponent` -> ``bytes``

        :param value: The value to convert
        :return: The data of ``value``
        """

        return value.calc_data

    @property
    def is_empty(self) -> bool:
        """
        :return: Whether this component's data is empty
        """

        return not len(self.calc_data)

    @classmethod
    def get_type(cls, *, type_id: int = None, extension: str = None) -> type[Self] | None:
        """
        Gets the subclass corresponding to a type ID or file extension if one is registered

        :param type_id: The type ID to search by, or
        :param extension: The file extension to search by
        :return: A subclass of this component with corresponding type ID or extension, or ``None``
        """

        if type_id is not None:
            if extension is not None:
                raise ValueError("too many parameters passed to get_type")

            return cls._type_ids.get(type_id, None)

    @classmethod
    def register(cls, var_type: type[Self], override: int = None):
        """
        Registers a subtype with this class for coercion

        :param var_type: The component subtype to register
        :param override: A type ID to use for registry that differs from that of the var type (defaults to no override)
        """

        cls._type_ids[var_type._type_id if override is None else override] = var_type

    def clear(self):
        """
        Clears this component's data
        """

        self.raw.calc_data = bytearray()

    def update(self):
        """
        Updates this component's metadata

        All attributes ``self.<name>`` are set to ``self.get_<name>()`` if possible.
        """

        names = dir(type(self))
        for name in names:
            if isinstance(getattr(type(self), name), Section) and (updater := f"get_{name}") in names:
                setattr(self, name, getattr(type(self), updater)(self))

    @Loader[bytes, bytearray, memoryview, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        """
        Loads a byte string or bytestream into this component

        :param data: The bytes to load
        """

        raise NotImplementedError

    def bytes(self) -> bytes:
        """
        :return: The bytes contained in this component
        """

        return self.raw.bytes()

    @Loader[dict]
    def load_dict(self, dct: dict):
        """
        Loads this component from a JSON dictionary representation

        :param dct: The dict to load
        """

        raise NotImplementedError

    load_json = load_dict

    def dict(self) -> dict:
        """
        :return: A JSON dictionary representation of this component
        """

        raise NotImplementedError

    json = dict

    @Loader[BinaryIO]
    def load_from_file(self, file: BinaryIO, *, offset: int = 0):
        """
        Loads this component from a file given a file pointer and offset

        :param file: A binary file to read from
        :param offset: The offset of the component to read
        """

        raise NotImplementedError

    @Loader[str]
    def load_string(self, string: str):
        """
        Loads this component from a string representation

        If there is no dedicated handler for a component type, all subclasses of the type will be considered.

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

        raise ValueError(f"could not parse '{string}' as a file component")

    def string(self) -> str:
        """
        :return: A string representation of this component
        """

        return format(self, "")

    def summary(self) -> str:
        """
        :return: A text summary of this component
        """

        raise NotImplementedError

    @classmethod
    def open(cls, filename: str) -> Self:
        """
        Creates a new component from a file given a filename

        :param filename: A filename to open
        :return: The (first) component stored in the file
        """

        raise NotImplementedError

    def save(self, filename: str = None, *, model: TIModel = TI_84PCE):
        """
        Saves this component as a complete file in the current directory given a filename and optional targeted model

        :param filename: A filename to save to (defaults to the component's name and extension)
        :param model: A `TIModel` to target (defaults to ``TI_84PCE``)
        """

        raise NotImplementedError

    def coerce(self):
        """
        Coerces this component to a subclass if possible using the component's type ID

        Valid types must be registered to be considered for coercion.
        """

        if self._type_id is None:
            if subclass := self.get_type(type_id=self.type_id):
                self.__class__ = subclass
                self.coerce()

            elif self.type_id != 0xFF:
                warn(f"Type ID 0x{self.type_id:02x} is not recognized; no coercion will occur.",
                     BytesWarning)


class TIFile(Dock):
    """
    Base class for TI files
    """

    magics: list[str] = []
    _magics: dict[str, type['TIFile']] = {}

    def __init__(self, *, name: str = "UNNAMED", data: bytes = None):
        """
        Creates an empty file with a specified name

        :param name: The name of the file (defaults to ``UNNAMED``)
        :param data: The file's data (defaults to empty)
        """

        self.name = name

        if data:
            self.load_bytes(data)

    def __bool__(self) -> bool:
        """
        :return: Whether this file is empty
        """

        return not len(self)

    def __bytes__(self) -> bytes:
        """
        :return: The bytes contained in this file
        """

        return self.bytes()

    def __copy__(self) -> 'TIFile':
        """
        :return: A copy of this var
        """

        new = self.__class__()
        new.load_bytes(self.bytes())
        return new

    def __eq__(self, other):
        """
        Determines if two files are identical

        :param other: The file to check against
        :return: Whether this file is equal to ``other``
        """

        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __format__(self, format_spec: str) -> str:
        return hex_format(self.bytes(), format_spec)

    def __init_subclass__(cls, /, register=False, **kwargs):
        super().__init_subclass__(**kwargs)

        if register:
            TIFile.register(cls)

    def __len__(self):
        """
        :return: The total length of this file in bytes
        """

        return len(self.bytes())

    @property
    def checksum(self) -> bytes:
        """
        The checksum for the file
        """

        raise NotImplementedError

    @property
    def is_empty(self) -> bool:
        """
        :return: Whether this file is empty
        """

        raise NotImplementedError

    @classmethod
    def get_type(cls, magic: str) -> type['TIFile'] | None:
        """
        Gets the subclass corresponding to file magic if one is registered

        :param magic: The file magic to search by
        :return: A subclass of `TIFile` with corresponding file magic or ``None``
        """

        return cls._magics.get(magic)

    @classmethod
    def register(cls, file_type: type['TIFile']):
        """
        Registers a subtype with this class for coercion

        :param file_type: The `TIFile` subtype to register
        """

        for magic in file_type.magics:
            cls._magics[magic] = file_type

    def get_extension(self, model: TIModel = TI_84PCE) -> str:
        """
        Determines the file extension for a targeted model based on its contents

        :param model: The model to target (defaults to this file's minimum supported model)
        :return: The file's extension
        """

        raise NotImplementedError

    def get_filename(self, model: TIModel = TI_84PCE):
        """
        Determines the filename based on the instance name and targeted model

        The filename is the concatenation of the name and extension (see `.get_extension`).

        :param model: The model to target (defaults to this file's minimum supported model)
        :return: The filename
        """

        return f"{self.name or 'UNNAMED'}.{self.get_extension(model)}"

    def supported_by(self, model: TIModel) -> bool:
        """
        Determines whether this file supports a given model

        See `.targets` to check models this file explicitly targets.

        :param model: The model to check support for
        :return: Whether ``model`` supports this file
        """

        raise NotImplementedError

    def targets(self, model: TIModel) -> bool:
        """
        Determines whether this file targets a given model

        See `.supported_by` to check models this file _can_ be sent to.

        :param model: The model to check as a target
        :return: Whether ``model`` is targeted by this file
        """

        raise NotImplementedError

    @Loader[bytes, bytearray, memoryview, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        """
        Loads a byte string or bytestream into this file

        :param data: The bytes to load
        """

        if hasattr(data, "read"):
            data = BytesIO(data.read())

        else:
            data = BytesIO(data)

        for magic in self._magics:
            if data.read(len(magic)) == magic.encode():
                self.__class__ = self.get_type(magic)

                data.seek(-len(magic), 1)
                self.__init__(name=self.name, data=data.read())

                return

            data.seek(-len(magic), 1)

        raise TypeError(f"unrecognized file magic: {data.read(8)}")

    def bytes(self) -> bytes:
        """
        :return: The bytes contained in this file
        """

        raise NotImplementedError

    @Loader[BinaryIO]
    def load_file(self, file: BinaryIO):
        """
        Loads this file from a file pointer

        :param file: A binary file to read from
        """

        self.load_bytes(file.read())

    def summary(self) -> str:
        """
        :return: A text summary of this file
        """

        raise NotImplementedError

    @classmethod
    def open(cls, filename: str) -> 'TIFile':
        """
        Creates a new file given a filename

        :param filename: A filename to open
        :return: The file
        """

        with open(filename, 'rb') as file:
            ti_file = cls(name=Path(filename).stem)
            ti_file.load_bytes(file.read())

            return ti_file

    def save(self, filename: str = None, model: TIModel = TI_84PCE):
        """
        Saves this file given a filename

        :param filename: A filename to save to (defaults to the file's name and extension)
        :param model: The model to target (defaults to ``TI_84PCE``)
        """
        try:
            if not self.supported_by(model):
                warn(f"The {model} does not support this file.",
                     UserWarning)

        except NotImplementedError:
            pass

        with open(filename or self.get_filename(model), 'wb+') as file:
            file.write(self.bytes())


__all__ = ["TIComponent", "TIFile"]
