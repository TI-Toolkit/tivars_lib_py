import numpy as np
import warnings

from PIL import ImageFile
from tivars import TIVar
from tivars.types.picture import PictureEntry


def accept(prefix):
    return prefix[:8] in (b"**TI82**", b"**TI83**", b"**TI83F*")


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


class TIDecoder(ImageFile.PyDecoder):
    def decode(self, buffer):
        var = TIVar()
        var.load_bytes(buffer)
        self.set_as_raw(np.asarray(var.entries[0].array(), dtype=np.uint8))

        return -1, 0
