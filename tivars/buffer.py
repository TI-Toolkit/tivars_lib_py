import re

from abc import abstractmethod
from typing import BinaryIO, Iterator


class Buffer:
    def __init__(self, width: int = None, default: bytes = None):
        self._width = width
        self._default = default.ljust(width, b'\x00')

    def __set_name__(self, owner, name: str):
        self._name = f"_{name}"

    def __get__(self, instance, owner: type = None) -> 'Buffer' | bytes | bytearray:
        if instance is None:
            return self

        if self._width is None:
            default = self._default or bytearray()

        else:
            default = self._default or bytes(self._width)

        return getattr(instance, self._name, default)

    def __set__(self, instance, value: bytes | bytearray):
        if self._width is not None:
            if len(value) > self._width:
                raise OverflowError("Value is too large for this buffer.")
            else:
                value = value.ljust(self._width, b'\x00')

        setattr(instance, self._name, value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def width(self) -> int:
        return self._width


class BoolBuffer(Buffer):
    def __init__(self, default: bool = False):
        super().__init__(1, bytes([default]))

    def __get__(self, instance, owner: type = None) -> 'BoolBuffer' | bool:
        if instance is None:
            return self

        return super().__get__(instance, owner) != b'\x00'

    def __set__(self, instance, value: bool):
        super().__set__(instance, bytes([value]))


class IntBuffer(Buffer):
    def __init__(self, width: int = 0, default: int = 0):
        super().__init__(width, bytes([default]))

    def __get__(self, instance, owner: type = None) -> 'IntBuffer' | int:
        if instance is None:
            return self

        return int.from_bytes(super().__get__(instance, owner), 'little')

    def __set__(self, instance, value: int):
        try:
            super().__set__(instance, int.to_bytes(value, self._width, 'little'))
        except OverflowError:
            raise OverflowError("Value is too large for this buffer.")


class StringBuffer(Buffer):
    def __init__(self, width: int = 0, default: str = None):
        super().__init__(width, default.encode('utf8'))

    def __get__(self, instance, owner: type = None) -> 'Buffer' | str:
        if instance is None:
            return self

        return super().__get__(instance, owner).decode('utf8')

    def __set__(self, instance, value: str):
        super().__set__(instance, value.encode('utf8'))


class NameBuffer(StringBuffer):
    def __set__(self, instance, value):
        varname = value[:8].upper()
        varname = re.sub(r"(\u03b8|\u0398|\u03F4|\u1DBF)", "[", varname)
        varname = re.sub(r"[^[a-zA-Z0-9]", "", varname)

        if not value or value[0].isnumeric():
            raise ValueError(f"Var has invalid name: {value} -> {varname}.")

        super().__set__(instance, varname)


class Section:
    def __bytes__(self) -> bytes:
        return self.bytes()

    def __str__(self):
        return self.string()

    @abstractmethod
    def export(self, **params) -> bytes:
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

    def load_buffer(self, buffer: 'Buffer', data: Iterator[bytes], width: int = None):
        width = buffer.width or width
        setattr(self, buffer.name, bytes(byte for byte, _ in zip(data, range(width))).ljust(width, b'\x00'))

    def load_bytes(self, data: bytes | Iterator[bytes]):
        data = iter(data)
        for attr in vars(Section).values():
            if isinstance(attr, Buffer):
                self.load_buffer(attr, data)

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

    @property
    def width(self) -> int:
        return sum(attr.width for attr in vars(Section).values() if isinstance(attr, Buffer))

    # Timeout corner for PyCharm's type checker
    def bytes(self) -> bytes:
        return b''.join(getattr(self, attr.name) for attr in vars(Section).values() if isinstance(attr, Buffer))


__all__ = ["Buffer", "BoolBuffer", "IntBuffer", "StringBuffer", "NameBuffer", "Section"]
