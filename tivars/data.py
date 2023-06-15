import copy
import inspect

from math import ceil
from typing import TypeVar
from warnings import warn


_T = TypeVar('_T')


class Converter:
    """
    Abstract base class for data section converters
    """

    _T = _T

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        """
        Converts `bytes` -> `_T`

        :param data: The raw bytes to convert
        :param instance: The instance which contains the data section (usually unused)
        :return: An instance of `_T`
        """

        raise NotImplementedError

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        """
        Converts  `_T` -> `bytes`

        :param value: The value to convert
        :param instance: The instance which contains the data section (usually unused)
        :return: A string of bytes
        """

        raise NotImplementedError


class Bytes(Converter):
    """
    No-op converter for data sections best interpreted as raw bytes
    """

    _T = bytes

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        """
        Converts `bytes` -> `bytes` (no-op)

        :param data: The raw bytes to convert
        :param instance: The instance which contains the data section (unused)
        :return: The bytes in `data`, unchanged
        """

        return data

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        """
        Converts `bytes` -> `bytes` (no-op)

        :param value: The value to convert
        :param instance: The instance which contains the data section (unused)
        :return: The bytes in `value`, unchanged
        """

        return value


class Boolean(Converter):
    """
    Converter for data sections best interpreted as boolean flags

    Expects the data section to be width one
    """

    _T = bool

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        """
        Converts `bytes` -> `bool`, where any nonzero value is truthy

        :param data: The raw bytes to convert
        :param instance: The instance which contains the data section (unused)
        :return: Whether `data` is nonzero
        """

        return data != b'\x00'

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        """
        Converts `bool` -> `bytes`, where `b'\x80'` is truthy and `b'\x00'` is falsy

        :param value: The value to convert
        :param instance: The instance which contains the data section (unused)
        :return: `b'\x80'` if `value` is truthy else `b'\x00'`
        """

        return b'\x80' if value else b'\x00'


class Integer(Converter):
    """
    Converter for data sections best interpreted as integers

    Integers are always little-endian, unsigned, and at most two bytes
    """

    _T = int

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        """
        Converts `bytes` -> `int`

        :param data: The raw bytes to convert
        :param instance: The instance which contains the data section (unused)
        :return: The little-endian integer given by `data`
        """

        return int.from_bytes(data, 'little')

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        """
        Converts `int` -> `bytes`

        For implementation reasons, the output of this converter is always two bytes wide

        :param value: The value to convert
        :param instance: The instance which contains the data section (unused)
        :return: The little-endian representation of `value`
        """

        return int.to_bytes(value, 2, 'little')


class String(Converter):
    """
    Converter for data sections best interpreted as strings

    Strings are encoded in utf-8
    """

    _T = str

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        """
        Converts `bytes` -> `str`

        :param data: The raw bytes to convert
        :param instance: The instance which contains the data section (unused)
        :return: The utf-8 decoding of `data` with trailing null bytes removed
        """

        return data.decode('utf8').rstrip('\0')

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        """
        Converts `str` -> `bytes`

        :param value: The value to convert
        :param instance: The instance which contains the data section (unused)
        :return: The utf-8 encoding of `value`
        """

        return value.encode('utf8')


class Section:
    """
    Data section class which handles conversion between bytes and appropriate data types

    A data section is given by its length and type converter
    Their primary function is to permit the user to read and write data sections as their natural data types

    A priori, a data section does not correspond to any one part of a var file
    Individual sections are instead stitched together to yield a var file's contents

    Distinct data sections are entirely independent, which is useful for sections which may vary in length
    To construct sections which point to a portion of another section, see the `View` class

    Data sections can be declared by decorating methods:
    ```py
    @Section(length, Converter)
    def data_section(self) -> _T:
        \"\"\"
        Docstring
        \"\"\"
    ```

    An optional second parameter can be passed, wherein the method is used as a pre-converter before `Converter.set`
    """

    def __init__(self, length: int = None, converter: type[Converter] = None):
        """
        Define a new data section given a length and type converter

        :param length: The length of the section (defaults to `None`, i.e. unbounded)
        :param converter: The type converter for the section (defaults to `Bytes`)
        """

        self._converter = converter or Bytes
        self._get, self._set = self._converter.get, self._converter.set
        self._length = length

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

        if self._length is not None:
            if len(value) > self._length:
                warn(f"Value {value} is too wide for this buffer; truncating to {value[:self._length]}.",
                     BytesWarning)
                value = value[:self._length]

            value = value.ljust(self._length, b'\x00')

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
    def length(self) -> int | None:
        return self._length


class View(Section):
    """
    Data view class which handles conversion between portions of data sections and appropriate data types

    A data view is given by its target data section, type converter, and indices within the target
    Indices must be contiguous and forward-facing

    Data views are effectively pointers to the data sections they view, converting data in and out as specified
    Note that data views cannot target other data views; this is done for implementation simplicity

    Data views can be declared by decorating methods:
    ```py
    @View(section, Converter)
    def data_view(self) -> _T:
        \"\"\"
        Docstring
        \"\"\"
    ```

    An optional second parameter can be passed, wherein the method is used as a pre-converter before `Converter.set`
    """

    def __init__(self, target: Section, converter: type[Converter] = None, indices: slice = slice(None)):
        """
        Define a new data view given a data section to watch, a type converter, and the portion of the section to view

        :param target: The data section to view
        :param converter: The type converter for the view (defaults to `Bytes`)
        :param indices: The slice of the data section to view (defaults to the entire section)
        """

        super().__init__(None, converter)

        self._target = target
        self._indices = indices

    def __get__(self, instance, owner: type = None) -> _T:
        if instance is None:
            return self

        return self._get(getattr(instance.raw, self._target.name)[self._indices], instance)

    def __set__(self, instance, value: _T):
        value = self._set(value, instance)

        if self.length is not None:
            value = value[:self.length].rjust(self.length, b'\x00')

        getattr(instance.raw, self._target.name)[self._indices] = value

    def __getitem__(self, indices: slice) -> 'View':
        return self.__class__(self._target, self._converter, indices)

    @property
    def length(self) -> int | None:
        if self._target.length is None:
            if (self._indices.step or 1) > 0:
                if (self._indices.start or 0) >= 0 and (self._indices.stop is None or self._indices.stop < 0):
                    return None

            else:
                if (self._indices.stop or 0) >= 0 and (self._indices.start is None or self._indices.start < 0):
                    return None

            return max(ceil(((self._indices.stop or 0) - (self._indices.start or 0)) // (self._indices.step or 1)), 0)

        else:
            return len(range(*self._indices.indices(self._target.length)))


class Dock:
    """
    Base class to inherit to implement the loader system
    """

    loaders = {}

    def load(self, data):
        """
        Loads data into an instance by delegating to `Loader` methods based on the input's type

        :param data: Any type which the instance might accept
        """
        for loader_types, loader in self.loaders.items():
            if any(isinstance(data, loader_type) for loader_type in loader_types):
                loader(self, data)
                return

        raise TypeError(f"could not find valid loader for type {type(data)}")


class Loader:
    """
    Function decorator to identify methods as data loaders for `Dock` instances

    Specify the loader's accepted type(s) using brackets:
    ```py
    @Loader[int]
    def load_int(self, data: int):
        ...
    ```
    """

    types = ()

    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kwargs):
        pass

    def __class_getitem__(cls, item: tuple[type, ...] | type) -> type:
        try:
            return type("Loader", (Loader,), {"types": tuple(item)})

        except TypeError:
            return type("Loader", (Loader,), {"types": (item,)})

    def __set_name__(self, owner, name: str):
        owner.loaders = owner.loaders | {self.types: self._func}
        setattr(owner, name, self._func)


__all__ = ["Section", "View", "Dock", "Loader",
           "Converter", "Bytes", "Boolean", "Integer", "String"]
