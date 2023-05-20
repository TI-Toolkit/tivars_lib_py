import copy
import inspect

from math import ceil
from typing import TypeVar
from warnings import warn


_T = TypeVar('_T')


class Converter:
    _T = _T

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        raise NotImplementedError

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        raise NotImplementedError


class Bytes(Converter):
    _T = bytes

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return data

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return value


class Boolean(Converter):
    _T = bool

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return data == b'\x80'

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return b'\x80' if value else b'\x00'


class Integer(Converter):
    _T = int

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return int.from_bytes(data, 'little')

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(value, 2, 'little')


class String(Converter):
    _T = str

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return data.decode('utf8').rstrip('\0')

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return value.encode('utf8')


class Section:
    def __init__(self, width: int = None, converter: type[Converter] = None):
        self._converter = converter or Bytes
        self._get, self._set = self._converter.get, self._converter.set
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

        return self._get(getattr(instance.raw, self._name), instance)

    def __set__(self, instance, value: _T):
        value = self._set(value, instance)

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
            case 2: new._set = lambda value, instance, _set=new._set: _set(func(instance, value), instance)
            case _: raise TypeError("Section and View function definitions can only take 1 or 2 parameters.")

        return new

    @property
    def name(self) -> str:
        return self._name

    @property
    def width(self) -> int | None:
        return self._width


class View(Section):
    def __init__(self, target: Section, converter: type[Converter] = None, indices: slice = slice(None)):
        super().__init__(None, converter)

        self._target = target
        self._indices = indices

    def __get__(self, instance, owner: type = None) -> _T:
        if instance is None:
            return self

        return self._get(getattr(instance.raw, self._target.name)[self._indices], instance)

    def __set__(self, instance, value: _T):
        value = self._set(value, instance)

        if self.width is not None:
            value = value[:self.width].rjust(self.width, b'\x00')

        getattr(instance.raw, self._target.name)[self._indices] = value

    def __getitem__(self, indices: slice) -> 'View':
        return self.__class__(self._target, self._converter, indices)

    @property
    def width(self) -> int | None:
        if self._target.width is None:
            if (self._indices.step or 1) > 0:
                if (self._indices.start or 0) >= 0 and (self._indices.stop is None or self._indices.stop < 0):
                    return None

            else:
                if (self._indices.stop or 0) >= 0 and (self._indices.start is None or self._indices.start < 0):
                    return None

            return max(ceil(((self._indices.stop or 0) - (self._indices.start or 0)) // (self._indices.step or 1)), 0)

        else:
            return len(range(*self._indices.indices(self._target.width)))


class Raw:
    def bytes(self) -> bytes:
        return b''.join(getattr(self, attr.lstrip("_")) for attr in self.__slots__ if not attr.startswith("__"))


class Dock:
    loaders = {}

    def load(self, data):
        for loader_types, loader in self.loaders.items():
            if any(isinstance(data, loader_type) for loader_type in loader_types):
                loader(self, data)
                return

        raise TypeError(f"could not find valid loader for type {type(data)}")


class Loader:
    types = ()

    def __init__(self, func):
        self._func = func

    def __class_getitem__(cls, item: tuple[type, ...]) -> type:
        return type("Loader", (Loader,), {"types": item})

    def __set_name__(self, owner, name: str):
        owner.loaders = owner.loaders | {self.types: self._func}
        setattr(owner, name, self._func)


__all__ = ["Section", "View", "Raw", "Dock", "Loader",
           "Converter", "Bytes", "Boolean", "Integer", "String"]
