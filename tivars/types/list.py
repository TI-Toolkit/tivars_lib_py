"""
Lists
"""


from collections.abc import Iterator, Sequence
from io import BytesIO
from typing import TypeAlias
from warnings import warn

from tivars.data import *
from tivars.models import *
from tivars.tokenizer import *
from tivars.var import TIEntry
from .complex import *
from .real import *


class ListName(Name):
    """
    Converter for the name section of lists

    List names can be ``L1`` - ``L6`` or a string of five alphanumeric characters that do not start with a digit.
    The special name and token ``IDList`` is also used (but is planned to be relegated to a separate type).
    """
    @classmethod
    def get(cls, data: bytes, **kwargs) -> str:
        """
        Converts ``bytes`` -> ``str`` as done by the memory viewer

        :param data: The raw bytes to convert
        :return: The list name contained in `data`
        """

        if data[0] == 0x5D:
            if data[1] < 6:
                return super().get(data)

            elif data[1] == 0x40:
                return "IDList"

            data = data[1:]

        return super().get(data)

    @classmethod
    def set(cls, value: str, **kwargs) -> bytes:
        """
        Converts ``str`` -> ``bytes`` to match appearance in the memory viewer

        :param value: The value to convert
        :return: The name encoding of ``value``
        """

        # TI-ASCII hack
        varname = value.upper().replace("]", "|L")
        if not varname.startswith("|L"):
            varname = "|L" + varname

        if "IDList" in varname:
            return b'\x5D\x40'

        else:
            if len(varname) > (7 if varname.startswith("|L") else 5):
                warn(f"The list name '{varname}' is too long.",
                     UserWarning)

            return super().set(varname)


class TIList(TIEntry):
    """
    Base class for all list entries

    A list entry is a one-dimensional array of `RealEntry` or `ComplexEntry` elements.
    Exact types are supported.
    """

    _E: TypeAlias = TIEntry

    versions = [0x00, 0x0B, 0x10]
    extension = "8xl"

    min_calc_data_length = 2

    def __init__(self, init=None, *,
                 name: str = "L1",
                 version: int = None, archived: bool = None,
                 data: bytes = None):

        super().__init__(init, name=name, version=version, archived=archived, data=data)

    def __format__(self, format_spec: str) -> str:
        if format_spec.endswith("t"):
            return "{" + ",".join(format(entry, format_spec) for entry in self.list()) + "}"

        else:
            return "[" + ", ".join(format(entry, format_spec) for entry in self.list()) + "]"

    def __iter__(self) -> Iterator[_E]:
        return iter(self.list())

    @Section(8, ListName)
    def name(self) -> str:
        """
        The name of the entry

        Names must be 1 to 5 characters in length.
        The name can include any characters A-Z, 0-9, or θ.
        The name cannot start with a digit; for these lists, use ``L1`` - ``L6`` instead.
        """

    @Section()
    def calc_data(self) -> bytearray:
        pass

    @View(calc_data, Integer)[0:2]
    def length(self, value) -> int:
        """
        The length of the list

        TI-OS imposes a limit of 999.
        """

        if value > 999:
            warn(f"The list is too long ({value} > 999).",
                 UserWarning)

        return value

    @View(calc_data, Bytes)[2:]
    def data(self) -> bytes:
        pass

    @datamethod
    @classmethod
    def get_min_os(cls, data: bytes) -> OsVersion:
        it = zip(*[iter(data)] * cls._E.min_calc_data_length)
        return max(map(cls._E.get_min_os, it), default=OsVersions.INITIAL)

    @datamethod
    @classmethod
    def get_version(cls, data: bytes) -> int:
        it = zip(*[iter(data)] * cls._E.min_calc_data_length)
        version = max(map(cls._E.get_version, it), default=0x00)

        if version > 0x1B:
            return 0x10

        elif version == 0x1B:
            return 0x0B

        else:
            return 0x00

    def supported_by(self, model: TIModel) -> bool:
        return super().supported_by(model) and (self.get_version() <= 0x0B or model.has(TIFeature.ExactMath))

    @Loader[bytes, bytearray, memoryview, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        if self._E.min_calc_data_length and self.calc_data_length // self._E.min_calc_data_length != self.length:
            warn(f"The list has an unexpected length "
                 f"(expected {self.length}, got {self.calc_data_length // self._E.min_calc_data_length}).",
                 BytesWarning)

    @Loader[Sequence]
    def load_list(self, lst: Sequence[_E]):
        """
        Loads a sequence into this list

        :param lst: The list to load
        """

        self.length = len(lst)
        self.data = b''.join(entry.calc_data for entry in lst)
        self.coerce()

    def list(self) -> list[_E]:
        """
        :return: A ``list`` of the elements in this list
        """

        it = zip(*[iter(self.data)] * self._E.min_calc_data_length)
        return [self._E(data=data) for data in it]

    @Loader[str]
    def load_string(self, string: str):
        self.load_list([self._E(element) for element in "".join(string.strip("[]{}")).split(",")])

    def coerce(self):
        for type_id, entry_type in self._type_ids.items():
            if type_id == self.data[0] & 31:
                if issubclass(entry_type, RealEntry):
                    self.__class__ = TIRealList
                    return

                elif issubclass(entry_type, ComplexEntry):
                    self.__class__ = TIComplexList
                    return

                else:
                    warn(f"List contains invalid type '{entry_type}'; no coercion will occur.",
                         UserWarning)
                    return

        warn(f"List contains unrecognized type ID 0x{self.data[0] & 31}; no coercion will occur.",
             UserWarning)


class TIRealList(TIList, register=True):
    """
    Parser for lists of real numbers
    """

    _E: TypeAlias = RealEntry

    _type_id = 0x01


class TIComplexList(TIList, register=True):
    """
    Parser for lists of complex numbers
    """

    _E: TypeAlias = ComplexEntry

    _type_id = 0x0D


__all__ = ["TIList", "TIRealList", "TIComplexList"]
