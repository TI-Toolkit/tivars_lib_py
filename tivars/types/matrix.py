from io import BytesIO
from typing import ByteString, Iterator
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal


class TIMatrix(TIEntry, register=True):
    """
    Parser for the matrix type

    A `TIMatrix` is a two-dimensional array of `TIReal` elements.
    """

    extensions = {
        None: "8xm",
        TI_82: "82m",
        TI_83: "83m",
        TI_82A: "8xm",
        TI_82P: "8xm",
        TI_83P: "8xm",
        TI_84P: "8xm",
        TI_84T: "8xm",
        TI_84PCSE: "8xm",
        TI_84PCE: "8xm",
        TI_84PCEPY: "8xm",
        TI_83PCE: "8xm",
        TI_83PCEEP: "8xm",
        TI_82AEP: "8xm"
    }

    min_data_length = 2

    _type_id = b'\x02'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "[A]",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):
        """
        Creates an empty `TIMatrix` with specified meta and data values

        :param init: Data to initialize this matrix's data (defaults to `None`)
        :param for_flash: Whether this matrix supports flash chips (default to `True`)
        :param name: The name of this matrix (defaults to `[A]`)
        :param version: This matrix's version (defaults to `None`)
        :param archived: Whether this matrix is archived (defaults to `False`)
        :param data: This matrix's data (defaults to empty)
        """

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "":
                inner_sep, outer_sep = ", ", ", "
            case "t":
                inner_sep, outer_sep = ",", ""
            case _:
                return super().__format__(format_spec)

        return "[" + outer_sep.join(f"[{inner_sep.join(format(entry, format_spec)for entry in row)}]"
                                    for row in self.matrix()) + "]"

    def __iter__(self) -> Iterator[TIReal]:
        for row in self.matrix():
            for entry in row:
                yield entry

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        The width and height of the matrix each take a byte and are followed by sequential element data sections.
        """

    @View(data, Integer)[0:1]
    def width(self) -> int:
        """
        The number of columns in the matrix

        TI-OS imposes a limit of 99.
        """

    @View(data, Integer)[1:2]
    def height(self) -> int:
        """
        The number of rows in the matrix

        TI-OS imposes a limit of 99.
        """

    @property
    def size(self) -> int:
        """
        :return: The number of elements in the matrix
        """

        return self.width * self.height

    @Loader[ByteString, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        if self.data_length // TIReal.min_data_length != self.size:
            warn(f"The matrix has an unexpected size "
                 f"(expected {self.data_length // TIReal.min_data_length}, got {self.size}).",
                 BytesWarning)

    def load_data_section(self, data: BytesIO):
        width = int.from_bytes(width_byte := data.read(1), 'little')
        height = int.from_bytes(height_byte := data.read(1), 'little')
        self.raw.data = bytearray(width_byte + height_byte + data.read(width * height))

    @Loader[list]
    def load_matrix(self, matrix: list[list[TIReal]]):
        """
        Loads a two-dimensional `list` into this matrix

        :param matrix: The matrix to load
        """

        if len({len(row) for row in matrix}) != 1:
            raise IndexError("matrix has uneven rows")

        self.load_bytes(bytes([len(matrix[0])]) + bytes([len(matrix)]) +
                        b''.join(entry.data for row in matrix for entry in row))

    def matrix(self) -> list[list[TIReal]]:
        """
        :return: A two-dimensional `list` of the elements in this matrix
        """

        matrix = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                entry = TIReal()

                entry.meta_length = self.meta_length
                entry.archived = self.archived

                index = self.width * i + j
                entry.data = self.data[entry.data_length * index + self.min_data_length:][:entry.data_length]
                row.append(entry)

            matrix.append(row.copy())

        return matrix

    @Loader[str]
    def load_string(self, string: str):
        matrix = []

        for string in ''.join(string.split())[1:-1].replace("],[", "][").split("]["):
            row = []
            for item in string.replace("[", "").replace("]", "").split(","):
                entry = TIReal()
                entry.load_string(item)
                row.append(entry)

            matrix.append(row.copy())

        self.load_matrix(matrix)

    def string(self) -> str:
        return format(self, "")


__all__ = ["TIMatrix"]
