from PIL import Image
from tivars import TIMonoPicture
from .common import *


class TI8xiImageFile(TIImageFile):
    _T = TIMonoPicture

    format = "8xi"
    format_description = "TI (e)Z80 Monochrome Picture Format"


class TI8xiEncoder(ImageFile.PyEncoder):
    _pushes_fd = True

    def encode(self, bufsize):
        img = TIMonoPicture()
        img.load_array(np.asarray(self.im).reshape((img.height, img.width)).tolist())
        data = img.export().bytes()

        return len(data), 0, data


def save(im, fp, *args, **kwargs):
    ImageFile._save(im, fp, [(TI8xiImageFile.format, (0, 0) + im.size, 0, im.mode)])


Image.register_open(TI8xiImageFile.format, TI8xiImageFile, accept)
Image.register_extension(TI8xiImageFile.format, "." + TI8xiImageFile.format)
Image.register_decoder(TI8xiImageFile.format, TIDecoder)

Image.register_save(TI8xiImageFile.format, save)
Image.register_encoder(TI8xiImageFile.format, TI8xiEncoder)
