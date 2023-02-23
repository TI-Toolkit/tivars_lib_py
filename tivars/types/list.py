import re

from typing import ByteString
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIType
from .numeric import TIReal, TIComplex


class ListVar(TIType):
    item_type = TIType

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

        if self.data_length // self.item_type.data.width != self.length:
            warn(f"The list has an unexpected length "
                 f"(expected {self.data_length // self.item_type.data.width}, got {self.length}).",
                 BytesWarning)

    def load_list(self, lst: list[item_type]):
        self.clear()
        self.data += int.to_bytes(len(lst), 2, 'little')

        for entry in lst:
            self.data += entry.data

    def list(self) -> list[item_type]:
        lst = []
        for i in range(self.length):
            entry = self.item_type()

            entry.meta_length = self.meta_length
            entry.archived = self.archived

            entry.data = self.data[entry.data_length * i + 2:][:entry.data_length]
            lst.append(entry)

        return lst

    def load_string(self, string: str):
        lst = []

        for string in ''.join(string.strip("[]").split()).split(","):
            entry = self.item_type()
            entry.load_string(string)
            lst.append(entry)

        self.load_list(lst)

    def string(self) -> str:
        return f"[{', '.join(str(entry) for entry in self.list())}]"


class TIRealList(ListVar):
    item_type = TIReal

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


class TIComplexList(ListVar):
    item_type = TIComplex

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
