from PIL import Image
from tivars import TIPicture
from .common import *


class TI8ciImageFile(TIImageFile):
    _T = TIPicture

    format = "8ci"
    format_description = "TI (e)Z80 Color Picture Format"


class TI8ciEncoder(ImageFile.PyEncoder):
    _pushes_fd = True

    def encode(self, bufsize):
        img = TIPicture()
        img.load_array(np.asarray(self.im).reshape((img.height, img.width)).tolist())
        data = img.export().bytes()

        return len(data), 0, data


def save(im, fp, *args, **kwargs):
    ImageFile._save(im, fp, [(TI8ciImageFile.format, (0, 0) + im.size, 0, im.mode)])


Image.register_open(TI8ciImageFile.format, TI8ciImageFile, accept)
Image.register_extension(TI8ciImageFile.format, "." + TI8ciImageFile.format)
Image.register_decoder(TI8ciImageFile.format, TIDecoder)

Image.register_save(TI8ciImageFile.format, save)
Image.register_encoder(TI8ciImageFile.format, TI8ciEncoder)
