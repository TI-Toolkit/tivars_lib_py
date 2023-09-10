from PIL import Image
from tivars import TIMonoPicture
from .common import *


class TI8xiImageFile(TIImageFile):
    _T = TIMonoPicture

    format = "8xi"
    format_description = "TI (e)Z80 Monochrome Picture Format"


Image.register_open(TI8xiImageFile.format, TI8xiImageFile, accept)
Image.register_extension(TI8xiImageFile.format, TI8xiImageFile.extension)
Image.register_decoder(TI8xiImageFile.format, TIDecoder)
