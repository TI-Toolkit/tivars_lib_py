import io
import re

from typing import ByteString, Iterator
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal, TIComplex


class ListEntry(TIEntry):
    _E = TIEntry

    min_data_length = 2

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "t": return f"{{{','.join(format(entry, 't') for entry in self.list())}}}"
            case _: return f"[{', '.join(format(entry, format_spec) for entry in self.list())}]"

    def __iter__(self) -> Iterator[_E]:
        return iter(self.list())

    @Section(8, String)
    def name(self, value) -> str:
        """
        The name of the entry

        Must be 1 to 5 characters in length
        Can include any characters A-Z, 0-9, or Θ
        Cannot start with a digit
        """

        varname = value[:5].upper()
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "[", varname)
        varname = re.sub(r"[^[a-zA-Z0-9]", "", varname)

        if not varname or varname[0].isnumeric():
            warn(f"Var has invalid name: {varname}.",
                 BytesWarning)

        return varname

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the length of the list, followed by sequential variable data sections
        """

    @View(data, Integer)[0:2]
    def length(self, value) -> int:
        """
        The length of the list

        Cannot exceed 999
        """

        if value > 999:
            warn(f"The list is too long ({value} > 999).",
                 UserWarning)

        return value

    def load_bytes(self, data: ByteString):
        super().load_bytes(data)

        if self.data_length // self._E.data.width != self.length:
            warn(f"The list has an unexpected length "
                 f"(expected {self.data_length // self._E.data.width}, got {self.length}).",
                 BytesWarning)

    def load_data_section(self, data: io.BytesIO):
        data_length = int.from_bytes(length_bytes := data.read(2), 'little')
        self.raw.data = bytearray(length_bytes + data.read(data_length))

    def load_list(self, lst: list[_E]):
        self.clear()
        self.data += int.to_bytes(len(lst), 2, 'little')

        for entry in lst:
            self.data += entry.data

    def list(self) -> list[_E]:
        lst = []
        for i in range(self.length):
            entry = self._E()

            entry.meta_length = self.meta_length
            entry.archived = self.archived

            entry.data = self.data[entry.data_length * i + 2:][:entry.data_length]
            lst.append(entry)

        return lst

    def load_string(self, string: str):
        lst = []

        for string in ''.join(string.strip("[]{}").split()).split(","):
            entry = self._E()
            entry.load_string(string)
            lst.append(entry)

        self.load_list(lst)

    def string(self) -> str:
        return format(self, "")


class TIRealList(ListEntry):
    _E = TIReal

    extensions = {
        None: "8xl",
        TI_82: "82l",
        TI_83: "83l",
        TI_82A: "8xl",
        TI_82P: "8xl",
        TI_83P: "8xl",
        TI_84P: "8xl",
        TI_84T: "8xl",
        TI_84PCSE: "8xl",
        TI_84PCE: "8xl",
        TI_84PCEPY: "8xl",
        TI_83PCE: "8xl",
        TI_83PCEEP: "8xl",
        TI_82AEP: "8xl"
    }

    _type_id = b'\x01'


class TIComplexList(ListEntry):
    _E = TIComplex

    extensions = {
        None: "8xl",
        TI_82: "",
        TI_83: "83l",
        TI_82A: "8xl",
        TI_82P: "8xl",
        TI_83P: "8xl",
        TI_84P: "8xl",
        TI_84T: "8xl",
        TI_84PCSE: "8xl",
        TI_84PCE: "8xl",
        TI_84PCEPY: "8xl",
        TI_83PCE: "8xl",
        TI_83PCEEP: "8xl",
        TI_82AEP: "8xl"
    }

    _type_id = b'\x0D'


__all__ = ["TIRealList", "TIComplexList"]
