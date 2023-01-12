import re

from abc import abstractmethod
from typing import BinaryIO
from warnings import warn


class Buffer:
    def __init__(self, width: int = None):
        self._width = width

    def __set_name__(self, owner, name: str):
        self._name = f"{name}_bytes"

    def __get__(self, instance, owner: type = None):
        if instance is None:
            return self

        return getattr(instance, self._name, bytearray() if self._width is None else bytes(self._width))

    def __set__(self, instance, value: bytes | bytearray):
        if self._width is not None:
            if len(value) > self._width:
                warn("Value is too large for this buffer.", BytesWarning)

            value = value[:self._width].ljust(self._width, b'\x00')

        setattr(instance, self._name, value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def width(self) -> int:
        return self._width


class BoolBuffer(Buffer):
    def __init__(self):
        super().__init__(1)

    def __get__(self, instance, owner: type = None):
        if instance is None:
            return self

        return super().__get__(instance, owner) != b'\x00'

    def __set__(self, instance, value: bool):
        super().__set__(instance, b'\x80' if value else b'\x00')


class IntBuffer(Buffer):
    def __init__(self, width: int = 0):
        super().__init__(width)

    def __get__(self, instance, owner: type = None):
        if instance is None:
            return self

        return int.from_bytes(super().__get__(instance, owner), 'little')

    def __set__(self, instance, value: int):
        try:
            super().__set__(instance, int.to_bytes(value, self._width, 'little'))
        except OverflowError:
            warn("Value is too large for this buffer.", BytesWarning)
            super().__set__(instance, int.to_bytes(value % (1 << self._width), self._width, 'little'))


class StringBuffer(Buffer):
    def __init__(self, width: int = 0):
        super().__init__(width)

    def __get__(self, instance, owner: type = None):
        if instance is None:
            return self

        return super().__get__(instance, owner).decode('utf8').rstrip('\0')

    def __set__(self, instance, value: str):
        super().__set__(instance, value.encode('utf8'))


class NameBuffer(StringBuffer):
    def __set__(self, instance, value):
        varname = value[:8].upper()
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "[", varname)
        varname = re.sub(r"[^[a-zA-Z0-9]", "", varname)

        if not varname or varname[0].isnumeric():
            warn(f"Var has invalid name: {varname}.", BytesWarning)

        super().__set__(instance, varname)


class Section:
    def __bytes__(self) -> bytes:
        return self.bytes()

    def __str__(self) -> str:
        return self.string()

    @property
    def width(self) -> int:
        return sum(attr.width for attr in vars(Section).values() if isinstance(attr, Buffer))

    @abstractmethod
    def bytes(self) -> bytes:
        pass

    def load(self, data):
        if isinstance(data, str):
            self.load_string(data)
            return

        try:
            self.load_file(data)
            return

        except AttributeError:
            self.load_bytes(data)

    @abstractmethod
    def load_bytes(self, data: bytes):
        pass

    def load_file(self, file: BinaryIO):
        self.load_bytes(file.read())

    @abstractmethod
    def load_string(self, string: str):
        pass

    def open(self, filename: str):
        with open(filename, 'rb') as file:
            self.load_bytes(file.read())

    def save(self, filename: str):
        with open(filename, 'wb+') as file:
            file.write(self.bytes())

    @abstractmethod
    def string(self) -> str:
        pass


__all__ = ["Buffer", "BoolBuffer", "IntBuffer", "StringBuffer", "NameBuffer", "Section"]
