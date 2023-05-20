from io import BytesIO
from typing import ByteString, Iterator
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal


class TIMatrix(TIEntry):
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

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "t":
                return "[" + \
                    ''.join(f"[{','.join(format(entry, 't') for entry in row)}]" for row in self.matrix()) \
                    + "]"
            case _:
                return "[" + \
                    ', '.join(f"[{', '.join(format(entry, format_spec) for entry in row)}]" for row in self.matrix()) \
                    + "]"

    def __iter__(self) -> Iterator[TIReal]:
        for row in self.matrix():
            for entry in row:
                yield entry

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the dimensions of the matrix, followed by sequential real variable data sections
        """

    @View(data, Integer)[0:1]
    def width(self) -> int:
        """
        The number of columns in the matrix

        Cannot exceed 255, though TI-OS imposes a limit of 99
        """

    @View(data, Integer)[1:2]
    def height(self) -> int:
        """
        The number of rows in the matrix

        Cannot exceed 255, though TI-OS imposes a limit of 99
        """

    @property
    def size(self) -> int:
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

    @Loader[list, ]
    def load_matrix(self, matrix: list[list[TIReal]]):
        if len({len(row) for row in matrix}) != 1:
            raise IndexError("matrix has uneven rows")

        self.load_bytes(int.to_bytes(len(matrix[0]), 1, 'little') + int.to_bytes(len(matrix), 1, 'little') +
                        b''.join(entry.data for row in matrix for entry in row))

    def matrix(self) -> list[list[TIReal]]:
        matrix = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                entry = TIReal()

                entry.meta_length = self.meta_length
                entry.archived = self.archived

                entry.data = self.data[entry.data_length * (self.width * i + j) + 2:][:entry.data_length]
                row.append(entry)

            matrix.append(row.copy())

        return matrix

    @Loader[str, ]
    def load_string(self, string: str):
        matrix = []

        for string in ''.join(string.split())[1:-1].split("],["):
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
