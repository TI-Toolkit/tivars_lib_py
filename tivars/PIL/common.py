import numpy as np
import warnings

from PIL import Image, ImageFile
from tivars import TIVar
from tivars.types.picture import PictureEntry


def accept(prefix):
    return prefix[:8] in (b"**TI82**", b"**TI83**", b"**TI83F*")


def register(file, encoder):
    Image.register_open(file.format, file, accept)
    Image.register_extension(file.format, "." + file.format)
    Image.register_decoder(file.format, TIDecoder)

    Image.register_save(file.format, file._save)
    Image.register_encoder(file.format, encoder)


class TIImageFile(ImageFile.ImageFile):
    _T = PictureEntry

    format = "8??"

    def _open(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")

            var = TIVar()
            var.load_bytes(self.fp.read())

            img = var.entries[0]
            if not isinstance(img, self._T):
                raise TypeError(f"image is not in .{self.format} format")

            self._size = (img.width, img.height)
            self.mode = img.pil_mode

            self.tile = [(self.format, (0, 0) + self.size, 0, None)]

    @classmethod
    def _save(cls, im, fp, format=None, **params):
        ImageFile._save(im, fp, format, [(cls.format, (0, 0) + im.size, 0, im.mode)])


class TIDecoder(ImageFile.PyDecoder):
    def decode(self, buffer):
        var = TIVar()
        var.load_bytes(buffer)
        self.set_as_raw(np.asarray(var.entries[0].array(), dtype=np.uint8))

        return -1, 0


class TIEncoder(ImageFile.PyEncoder):
    _pushes_fd = True

    _T = PictureEntry

    def encode(self, bufsize):
        img = self._T()
        img.load_array(np.asarray(self.im).reshape((img.height, img.width)).tolist())
        data = img.export().bytes()

        return len(data), 0, data
