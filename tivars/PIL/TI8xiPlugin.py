from tivars import TIMonoPicture
from .common import *


class TI8xiImageFile(TIImageFile):
    _T = TIMonoPicture

    format = "8xi"
    format_description = "TI (e)Z80 Monochrome Picture Format"


class TI8xiEncoder(TIEncoder):
    _T = TIMonoPicture


register(TI8xiImageFile, TI8xiEncoder)
