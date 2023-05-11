import io

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

    def load_bytes(self, data: ByteString):
        super().load_bytes(data)

        if self.data_length // TIReal.data.width != self.size:
            warn(f"The matrix has an unexpected size "
                 f"(expected {self.data_length // TIReal.data.width}, got {self.size}).",
                 BytesWarning)

    def load_data_section(self, data: io.BytesIO):
        width, height = int.from_bytes(data.read(1), 'little'), int.from_bytes(data.read(1), 'little')
        self.raw.data = bytearray(int.to_bytes(width, 2, 'little') + int.to_bytes(height, 2, 'little')
                                  + data.read(width * height))

    def load_matrix(self, matrix: list[list[TIReal]]):
        if len({len(row) for row in matrix}) != 1:
            raise IndexError("matrix has uneven rows")

        self.clear()
        self.data += int.to_bytes(len(matrix[0]), 2, 'little')
        self.data += int.to_bytes(len(matrix), 2, 'little')

        for row in matrix:
            for entry in row:
                self.data += entry.data

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
        return "[" + ', '.join(f"[{', '.join(str(entry) for entry in row)}]" for row in self.matrix()) + "]"


__all__ = ["TIMatrix"]
