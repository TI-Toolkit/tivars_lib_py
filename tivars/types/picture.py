from typing import ByteString, Iterator
from warnings import warn

from tivars.models import *
from tivars.tokenizer import TokenizedString
from ..data import *
from ..var import SizedEntry

RGB = tuple[int, int, int]


class L1(Converter):
    _T = tuple[int, ...]

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return tuple(255 * (1 - int(bit)) for bit in f"{data[0]:08b}")

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes(int("".join("0" if bit else "1" for bit in value), 2), 1, 'little')


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
    def nearest(cls, r: int, g: int, b: int) -> RGB:
        nearest = min(cls.palette, key=lambda x: (x[0] - r) ** 2 + (x[1] - g) ** 2 + (x[2] - b) ** 2)
        if nearest != (r, g, b):
            warn(f"The pixel {(r, g, b)} is not contained in the palette; using {nearest} as an approximation.",
                 UserWarning)

        return nearest

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return cls.palette[data[0] >> 4], cls.palette[data[0] & 15]

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return int.to_bytes((cls.palette.index(cls.nearest(*value[0])) << 4) +
                            cls.palette.index(cls.nearest(*value[1])), 1, 'little')


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
        return int.to_bytes(((value[1] >> 2 & 7) << 5) | value[2] >> 3, 1, 'little') + \
            int.to_bytes((value[0] & ~7) | (value[1] >> 5), 1, 'little')


class PictureEntry(SizedEntry):
    width = 0
    height = 0

    data_width = width
    data_height = height
    data_offset = 2

    pil_mode = None
    pixel_type = None
    has_color = True

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Pic1",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.length = self.min_data_length

    def __iter__(self) -> Iterator[pixel_type]:
        raise NotImplementedError

    @Loader[list, ]
    def load_array(self, arr: list[list[pixel_type]]):
        raise NotImplementedError

    def array(self) -> list[list[pixel_type]]:
        raise NotImplementedError


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

    min_data_length = 758

    width = 96
    height = 63

    data_width = width // 8
    data_height = height
    data_offset = 2

    pil_mode = "L"
    pixel_type = int
    has_color = False

    _type_id = b'\x07'

    def __iter__(self) -> Iterator[pixel_type]:
        for byte in self.data[self.data_offset:]:
            for bit in L1.get(byte, self):
                yield bit

    @Loader[list]
    def load_array(self, arr: list[list[pixel_type]]):
        self.raw.data[2:] = b''.join(L1.set(entry, self) for row in arr for entry in zip(*[iter(row)] * 8, strict=True))

    def array(self) -> list[list[pixel_type]]:
        return [[bw for col in range(self.data_width)
                 for bw in L1.get(self.data[self.data_width * row + col + self.data_offset:][:1], self)]
                for row in range(self.data_height)]

    def coerce(self):
        match self.length + 2:
            case self.min_data_length: pass
            case TIPicture.min_data_length: self.__class__ = TIPicture
            case TIImage.min_data_length: self.__class__ = TIImage
            case _: warn(f"Picture has unexpected length ({self.length}).",
                         BytesWarning)


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

    min_data_length = 21947

    width = 266
    height = 165

    data_width = width // 2
    data_height = height
    data_offset = 2

    pil_mode = "RGB"
    pixel_type = RGB

    def __iter__(self) -> Iterator[pixel_type]:
        for byte in self.data[self.data_offset:]:
            for rgb in RGBPalette.get(byte, self):
                yield rgb

    @Loader[list]
    def load_array(self, arr: list[list[pixel_type]]):
        self.raw.data[2:] = b''.join(RGBPalette.set(entry, self) for row in arr for entry in zip(row[::2], row[1::2]))

    def array(self) -> list[list[pixel_type]]:
        return [[rgb for col in range(self.data_width)
                 for rgb in RGBPalette.get(self.data[self.data_width * row + col + self.data_offset:][:1], self)]
                for row in range(self.data_height)]

    def coerce(self):
        match self.length + 2:
            case self.min_data_length: pass
            case TIMonoPicture.min_data_length: self.__class__ = TIMonoPicture
            case TIImage.min_data_length: self.__class__ = TIImage
            case _: warn(f"Picture has unexpected length ({self.length}).",
                         BytesWarning)


# Workaround until the token sheets are updated
class ImageName(TokenizedString):
    _T = str

    @classmethod
    def get(cls, data: bytes, instance) -> _T:
        return f"Image{data[1] + 1}"

    @classmethod
    def set(cls, value: _T, instance) -> bytes:
        return b"\x3C" + int.to_bytes(int(value[-1], 16) - 1, 1, 'little')


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

    min_data_length = 22247

    width = 133
    height = 83

    data_width = 2 * width + 2
    data_height = height
    data_offset = 3

    pil_mode = "RGB"
    pixel_type = RGB

    _type_id = b'\x1A'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.image_magic = b'\x81'

    def __iter__(self) -> Iterator[pixel_type]:
        for row in range(self.data_height - 1, -1, -1):
            for col in range(0, self.data_width - 2, 2):
                yield RGB565.get(self.data[self.data_width * row + col + self.data_offset:][:2], self)

    @Section(8, ImageName)
    def name(self) -> str:
        """
        The name of the entry

        Must be one of the image names: Image1 - Image0
        """

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

    @Loader[list]
    def load_array(self, arr: list[list[pixel_type]]):
        self.raw.data[3:] = b''.join(RGB565.set(entry, self) for row in arr[::-1] for entry in row + [(0, 0, 0)])

    def array(self) -> list[list[pixel_type]]:
        return [[RGB565.get(self.data[self.data_width * row + col + 3:][:2], self)
                 for col in range(0, self.data_width - 2, 2)]
                for row in range(self.data_height)][::-1]

    def coerce(self):
        match self.length + 2:
            case self.min_data_length: pass
            case TIMonoPicture.min_data_length: self.__class__ = TIMonoPicture
            case TIPicture.min_data_length: self.__class__ = TIPicture
            case _: warn(f"Image has unexpected length ({self.length}).",
                         BytesWarning)


__all__ = ["TIMonoPicture", "TIPicture", "TIImage",
           "L1", "RGBPalette", "RGB565"]
