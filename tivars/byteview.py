import copy
import inspect

from itertools import zip_longest
from math import ceil


class byteview:
    def __init__(self, view: 'byteview' = None, section: slice = slice(None)):
        if section.step not in (1, None):
            raise NotImplementedError("Byteviews do not support non-contiguous or reversed data sections.")

        self._view = view
        self._section = section

        self._takes = None
        self._returns = None

    def span(self, instance):
        if self._view is None:
            indices = list(range(len(instance)))[self._section]
            return indices[0], indices

        start, indices = self._view.span(instance)
        if indices := indices[self._section]:
            return indices[0], indices

        else:
            return start + (self._section.start or 0), []

    def get_bytes(self, instance):
        return byteview._get(self, instance, *self.span(instance))

    def _get(self, instance, start, indices):
        if self._view is None:
            return bytearray(instance[index] for index in indices)

        return self._view._get(instance, start, indices)

    def __get__(self, instance, owner: type = None):
        if instance is None:
            return self

        if self._returns is None:
            return self._get(instance, *self.span(instance))

        self.__set__(instance, value := self._returns(instance))
        return value

    def set_bytes(self, instance, value):
        byteview._set(self, instance, value, *self.span(instance), self.width is not None)

    def _set(self, instance, value, start, indices, fixed):
        if self._view is None:
            if fixed:
                if len(indices) < len(value):
                    raise ValueError(f"Value {value} is too wide for this buffer.")

                for index, byte in zip_longest(indices, value, fillvalue=0):
                    instance[index] = byte

            else:
                for _ in indices:
                    instance.pop(start)

                for byte in value:
                    instance.insert(start, byte)
                    start += 1
        else:
            self._view._set(instance, value, start, indices, fixed)

    def __set__(self, instance, value):
        if self._takes is not None:
            value = self._takes(instance, value)

        self._set(instance, value, *self.span(instance), self.width is not None)

    def __delete__(self, instance):
        self._set(instance, b'', *self.span(instance), self.width is not None)

    def __getitem__(self, section: slice):
        return self.__class__(self._view, section)

    def __copy__(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new

        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))

        return new

    def __call__(self, func):
        def e():
            pass

        def ed():
            """"""
            pass

        new = copy.copy(self)
        new.__doc__ = func.__doc__

        if func.__code__.co_code not in (e.__code__.co_code, ed.__code__.co_code):
            signature = inspect.signature(func)
            match len(signature.parameters):
                case 1: new._returns = func
                case 2: new._takes = func
                case _: raise TypeError("Function definitions for byteviews can only take 1 or 2 parameters.")

        return new

    @property
    def width(self) -> int:
        return max((self._section.stop or 0) - (self._section.start or 0), 0)


class dataview(byteview):
    @property
    def width(self) -> int | None:
        return None


class boolview(byteview):
    def _get(self, instance, start, indices):
        return super()._get(instance, start, indices) == b'\x80'

    def _set(self, instance, value, start, indices, fixed):
        super()._set(instance, (b'\x80' if value else b'\x00'), start, indices, fixed)


class intview(byteview):
    def _get(self, instance, start, indices):
        return int.from_bytes(super()._get(instance, start, indices), 'little')

    def _set(self, instance, value, start, indices, fixed):
        super()._set(instance, int.to_bytes(value, ceil(value.bit_length() / 8), 'little'), start, indices, fixed)


class stringview(byteview):
    def _get(self, instance, start, indices):
        return super()._get(instance, start, indices).decode('utf8').rstrip('\0')

    def _set(self, instance, value, start, indices, fixed):
        return super()._set(instance, value.encode('utf8'), start, indices, fixed)


class ByteArray(bytearray):
    def __getitem__(self, item):
        try:
            return item.get_bytes(self)

        except AttributeError:
            try:
                return self.__getitem__(getattr(self.__class__, item))

            except (AttributeError, TypeError):
                return super().__getitem__(item)

    def __setitem__(self, item, value):
        try:
            item.set_bytes(self, value)

        except AttributeError:
            try:
                self.__setitem__(getattr(self.__class__, item), value)

            except (AttributeError, TypeError):
                super().__setitem__(item, value)


__all__ = ["byteview", "dataview", "boolview", "intview", "stringview",
           "ByteArray"]
