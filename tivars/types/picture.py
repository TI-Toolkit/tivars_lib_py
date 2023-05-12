from tivars.models import *
from ..data import *
from ..var import SizedEntry

RGB = tuple[int, int, int]


class L1(Converter):
    _T = tuple[int, ...]

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return tuple(255 * int(bit) for bit in f"{data[0]:08b}")

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(int("".join("1" if bit else "0" for bit in value), 2), 1, 'little')


class RGBPalette(Converter):
    _T = tuple[RGB, RGB]

    Blue = (0, 0, 255)
    Red = (255, 0, 0)
    Black = (0, 0, 0)
    Magenta = (255, 0, 255)
    Green = (0, 158, 0)
    Orange = (255, 142, 32)
    Brown = (182, 32, 0)
    Navy = (0, 0, 134)
    LtBlue = (0, 146, 255)
    Yellow = (255, 255, 0)
    White = (255, 255, 255)
    LtGray = (231, 227, 231)
    MedGray = (199, 195, 199)
    Gray = (142, 138, 142)
    DarkGray = (81, 85, 81)

    palette = [White, Blue, Red, Black, Magenta, Green, Orange, Brown, Navy, LtBlue, Yellow,
               White, LtGray, MedGray, Gray, DarkGray]

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return cls.palette[data[0] >> 4], cls.palette[data[0] & 15]

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes((cls.palette.index(value[0]) << 4) + cls.palette.index(value[1]), 1, 'little')


class RGB565(Converter):
    _T = RGB

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return (
            (data[1] >> 3) * 255 // 31,
            (((data[1] & 7) << 3) | (data[0] >> 5)) * 255 // 63,
            (data[0] & 31) * 255 // 31
        )

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(((value[1] // 4 & 7) << 5) + value[2] // 8, 1, 'little') + \
            int.to_bytes((value[0] // 8 << 3) | (value[1] // 4 >> 3), 1, 'little')


class PictureEntry(SizedEntry):
    width = 0
    height = 0

    pil_mode = "RGB"


class TIMonoPicture(PictureEntry):
    extensions = {
        None: "8xi",
        TI_82: "",
        TI_83: "",
        TI_82A: "8xi",
        TI_82P: "8xi",
        TI_83P: "8xi",
        TI_84P: "8xi",
        TI_84T: "8xi",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "",
        TI_83PCE: "",
        TI_83PCEEP: "",
        TI_82AEP: ""
    }

    width = 96
    height = 63

    pil_mode = "L"

    def load_bw_array(self, arr: list[list[int]]):
        self.raw.data[2:] = b''.join(L1.set(entry, self) for row in arr for entry in zip(*[iter(row)] * 8, strict=True))

    def bw_array(self) -> list[list[int]]:
        return [[bw for col in range(96) for bw in L1.get(self.data[96 * row + col + 2], self)]
                for row in range(63)]

    def coerce(self):
        if self.length != 1008:
            self.__class__ = TIPicture
            self.coerce()


class TIPicture(PictureEntry):
    flash_only = True

    extensions = {
        None: "8ci",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "8ci",
        TI_84PCE: "8ci",
        TI_84PCEPY: "8ci",
        TI_83PCE: "8ci",
        TI_83PCEEP: "8ci",
        TI_82AEP: "8ci"
    }

    width = 266
    height = 165

    def load_rgb_array(self, arr: list[list[RGB]]):
        self.raw.data[2:] = b''.join(RGBPalette.set(entry, self) for row in arr for entry in zip(row[::2], row[1::2]))

    def rgb_array(self) -> list[list[RGB]]:
        return [[rgb for col in range(133) for rgb in RGBPalette.get(self.data[133 * row + col + 2], self)]
                for row in range(165)]

    def coerce(self):
        if self.length != 21945:
            self.__class__ = TIImage


class TIImage(PictureEntry):
    flash_only = True

    extensions = {
        None: "8ca",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "8ca",
        TI_84PCE: "8ca",
        TI_84PCEPY: "8ca",
        TI_83PCE: "8ca",
        TI_83PCEEP: "8ca",
        TI_82AEP: "8ca"
    }

    width = 133
    height = 83

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the length of the remaining data as its first two bytes
        """

    @View(data, Bytes)[2:3]
    def image_magic(self) -> int:
        """
        Magic to identify the var as an image

        Always set to 0x81
        """

    def load_rgb_array(self, arr: list[list[RGB]]):
        self.raw.data[3:] = b''.join(RGB565.set(entry, self) for row in arr for entry in row)

    def rgb_array(self) -> list[list[RGB]]:
        return [[RGB565.get(self.data[268 * row + 2 * col + 3:][:2], self) for col in range(133)]
                for row in range(82, -1, -1)]


__all__ = ["TIMonoPicture", "TIPicture", "TIImage",
           "L1", "RGBPalette", "RGB565"]
