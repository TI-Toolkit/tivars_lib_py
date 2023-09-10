from PIL import Image
from tivars import TIPicture
from .common import *


class TI8ciImageFile(TIImageFile):
    _T = TIPicture

    format = "8ci"
    format_description = "TI (e)Z80 Color Picture Format"


Image.register_open(TI8ciImageFile.format, TI8ciImageFile, accept)
Image.register_extension(TI8ciImageFile.format, TI8ciImageFile.extension)
Image.register_decoder(TI8ciImageFile.format, TIDecoder)
