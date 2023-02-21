import copy
import inspect

from math import ceil
from typing import Callable, TypeVar
from warnings import warn


_E = TypeVar('_E')
_T = TypeVar('_T')
Converter = tuple[Callable[[_T, _E], bytes], Callable[[bytes, _E], _T]]


Bytes = (lambda value, instance: value,
         lambda data, instance: data)

Boolean = (lambda value, instance: b'\x80' if value else b'\x00',
           lambda data, instance: data == b'\x80')

Integer = (lambda value, instance: int.to_bytes(value, ceil(value.bit_length() / 8), 'little'),
           lambda data, instance: int.from_bytes(data, 'little'))

String = (lambda value, instance: value.encode('utf8'),
          lambda data, instance: data.decode('utf8').rstrip('\0'))


class Section:
    def __init__(self, width: int = None, converter: Converter = None):
        self._in, self._out = converter.converter() if hasattr(converter, "converter") else converter or Bytes
        self._width = width

    def __copy__(self) -> 'Section':
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo) -> 'Section':
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))

        return new

    def __set_name__(self, owner, name: str):
        self._name = name

    def __get__(self, instance, owner: type = None) -> _T:
        if instance is None:
            return self

        return self._out(getattr(instance.raw, self._name), instance)

    def __set__(self, instance, value: _T):
        value = self._in(value, instance)

        if self._width is not None:
            if len(value) > self._width:
                warn(f"Value {value} is too wide for this buffer; truncating to {value[:self._width]}.",
                     BytesWarning)
                value = value[:self._width]

            value = value.ljust(self._width, b'\x00')

        setattr(instance.raw, self._name, value)

    def __call__(self, func) -> 'Section':
        new = copy.copy(self)
        new.__doc__ = func.__doc__

        signature = inspect.signature(func)
        match len(signature.parameters):
            case 1: pass
            case 2: new._in = lambda value, instance, _in=new._in: _in(func(instance, value), instance)
            case _: raise TypeError("Data section function definitions can only take 1 or 2 parameters.")

        return new

    @property
    def name(self) -> str:
        return self._name

    @property
    def width(self) -> int | None:
        return self._width


class View:
    def __init__(self, target: Section, converter, indices: slice = slice(None)):
        self._target = target
        self._in, self._out = converter.converter() if hasattr(converter, "converter") else converter or Bytes
        self._indices = indices

    def __copy__(self) -> 'View':
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo) -> 'View':
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))

        return new

    def __get__(self, instance, owner: type = None) -> _T:
        if instance is None:
            return self

        return self._out(getattr(instance.raw, self._target.name)[self._indices], instance)

    def __set__(self, instance, value: _T):
        value = self._in(value, instance)

        if self.width is not None:
            if len(value) > self.width:
                warn(f"Value {value} is too wide for this buffer; truncating to {value[:self.width]}.",
                     BytesWarning)
                value = value[:self.width]

            value = value.rjust(self.width, b'\x00')

        getattr(instance.raw, self._target.name)[self._indices] = value

    def __getitem__(self, indices: slice) -> 'View':
        return self.__class__(self._target, (self._in, self._out), indices)

    def __call__(self, func) -> 'View':
        new = copy.copy(self)
        new.__doc__ = func.__doc__

        signature = inspect.signature(func)
        match len(signature.parameters):
            case 1: pass
            case 2: new._in = lambda value, instance, _in=new._in: _in(func(instance, value), instance)
            case _: raise TypeError("Data view function definitions can only take 1 or 2 parameters.")

        return new

    @property
    def width(self) -> int | None:
        if self._target.width is None:
            if (self._indices.step or 1) > 0 and (self._indices.stop is None or self._indices.stop < 0):
                return None

            if self._indices.start is None or self._indices.start < 0:
                return None

            return max(ceil(((self._indices.stop or 0) - (self._indices.start or 0)) // (self._indices.step or 1)), 0)

        else:
            return len(range(*self._indices.indices(self._target.width)))


class Raw:
    def bytes(self) -> bytes:
        return b''.join(getattr(self, attr.lstrip("_")) for attr in self.__slots__)


__all__ = ["Section", "View", "Raw", "Bytes", "Boolean", "Integer", "String"]
