from PIL import Image
from tivars import TIImage
from .common import *


class TI8caImageFile(TIImageFile):
    _T = TIImage

    format = "8ca"
    format_description = "TI (e)Z80 Image Format"


Image.register_open(TI8caImageFile.format, TI8caImageFile, accept)
Image.register_extension(TI8caImageFile.format, TI8caImageFile.extension)
Image.register_decoder(TI8caImageFile.format, TIDecoder)
