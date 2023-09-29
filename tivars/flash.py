from io import BytesIO
from typing import BinaryIO, ByteString, Iterator, Type
from warnings import warn

from tivars.models import *
from .data import *


class TIFlash:
    """
    Parser for flash files
    """

    class Raw:
        """
        Raw bytes container for `TIFlash`

        Any class with a distinct byte format requires its own `Raw` class to contain its data sections.
        Each data section must have a corresponding slot in `Raw` in order to use `Converter` classes.

        The `Raw` class must also contain a `bytes()` method specifying the order and visibility of the data sections.
        Additional methods can also be included, but should be callable from the outer class.
        """

        __slots__ = "magic", "revision", "flags", "object_type", "date", "name", "device_type", "data_type", "calc_data"

        @property
        def calc_data_size(self) -> bytes:
            pass

        @property
        def checksum(self) -> bytes:
            return int.to_bytes(sum(self.calc_data) & 0xFFFF, 2, 'little')

        @property
        def name_length(self) -> bytes:
            return bytes([len(self.name.rstrip(b'\x00'))])

        def bytes(self) -> bytes:
            """
            :return: The bytes contained in this file
            """

            return self.magic + self.revision + self.flags + self.object_type + self.date + \
                self.name_length + self.name + bytes(23) + self.device_type + self.data_type + bytes(24) + \
                self.calc_data_size + self.calc_data + self.checksum

    @Section(8, String)
    def magic(self) -> str:
        """
        The file magic for the flash file
        """
