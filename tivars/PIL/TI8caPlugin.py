from tivars import TIImage
from .common import *


class TI8caImageFile(TIImageFile):
    _T = TIImage

    format = "8ca"
    format_description = "TI (e)Z80 Image Format"


class TI8caEncoder(TIEncoder):
    _T = TIImage


register(TI8caImageFile, TI8caEncoder)
