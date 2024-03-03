"""
File headers
"""


from io import BytesIO
from typing import BinaryIO

from .data import *


class Header(Dock):
    """
    Base class for file headers
    """

    magics = set()
    """
    File magics which identify this header
    """

    class Raw:
        """
        Raw bytes container for headers

        Any class with a distinct byte format requires its own ``Raw`` class to contain its data sections.
        Each data section must have a corresponding slot in ``Raw`` in order to use `Converter` classes.

        The ``Raw`` class must also contain a ``bytes()`` method specifying the order of the data sections.
        Additional methods can also be included, but should be callable from the outer class.
        """

        __slots__ = "magic"

        def bytes(self) -> bytes:
            """
            :return: The bytes contained in this header
            """

            raise NotImplementedError

    def __init__(self, magic: str = None, data: bytes = None):
        """
        Creates an empty header

        :param magic: File magic at the start of the header (defaults to the model's magic)
        :param data: This header's data (defaults to empty)
        """

        self.raw = self.Raw()

    def __bytes__(self) -> bytes:
        """
        :return: The bytes contained in this header
        """

        return self.bytes()

    def __copy__(self) -> 'Header':
        """
        :return: A copy of this header
        """

        new = type(self)()
        new.load_bytes(self.bytes())
        return new

    def __eq__(self, other: 'Header') -> bool:
        """
        Determines if two headers have the same bytes

        :param other: The header to check against
        :return: Whether this header is equal to ``other``
        """

        try:
            return self.__class__ == other.__class__ and self.bytes() == other.bytes()

        except AttributeError:
            return False

    def __len__(self) -> int:
        """
        :return: The total length of this header's bytes
        """

        return len(self.bytes())

    @Section(8, String)
    def magic(self) -> str:
        """
        The file magic for the header
        """

    @Loader[bytes, bytearray, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        """
        Loads a byte string or bytestream into the header

        :param data: The source bytes
        """

        raise NotImplementedError

    def bytes(self) -> bytes:
        """
        :return: The bytes contained in this header
        """

        return self.raw.bytes()

    @Loader[BinaryIO]
    def load_from_file(self, file: BinaryIO):
        """
        Loads this header from a file given a file pointer

        :param file: A binary file to read from
        """

        self.load_bytes(file.read(len(self)))

    @classmethod
    def open(cls, filename: str) -> 'Header':
        """
        Creates a new header from a file given a filename

        :param filename: A filename to open
        :return: The header stored in the file
        """

        with open(filename, 'rb') as file:
            return cls(data=file.read())
