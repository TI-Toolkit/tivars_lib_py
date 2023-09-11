from PIL import Image
from tivars import TIImage
from .common import *


class TI8caImageFile(TIImageFile):
    _T = TIImage

    format = "8ca"
    format_description = "TI (e)Z80 Image Format"


class TI8caEncoder(ImageFile.PyEncoder):
    _pushes_fd = True

    def encode(self, bufsize):
        img = TIImage()
        img.load_array(np.asarray(self.im).reshape((img.height, img.width)).tolist())
        data = img.export().bytes()

        return len(data), 0, data


def save(im, fp, *args, **kwargs):
    ImageFile._save(im, fp, [(TI8caImageFile.format, (0, 0) + im.size, 0, im.mode)])


Image.register_open(TI8caImageFile.format, TI8caImageFile, accept)
Image.register_extension(TI8caImageFile.format, "." + TI8caImageFile.format)
Image.register_decoder(TI8caImageFile.format, TIDecoder)

Image.register_save(TI8caImageFile.format, save)
Image.register_encoder(TI8caImageFile.format, TI8caEncoder)
