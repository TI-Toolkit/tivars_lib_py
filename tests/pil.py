import io
import unittest

from tivars.types.picture import *

try:
    from PIL import Image
    from tivars.PIL import *

except ImportError:
    raise unittest.SkipTest("PIL not installed")


try:
    import numpy as np

except ImportError:
    raise unittest.SkipTest("NumPy not installed")


class PILTests(unittest.TestCase):
    def test_8xi(self):
        ti_img = TIMonoPicture.open("tests/data/var/BartSimpson.8xi")

        arr = np.asarray(ti_img.array(), dtype=np.uint8)
        img = Image.open("tests/data/var/BartSimpson.8xi")

        self.assertEqual((np.asarray(Image.fromarray(arr)) == np.asarray(img)).all(), True)

        img.save(buf := io.BytesIO(), "8xi")
        buf.seek(0)

        self.assertEqual(buf.read()[72:-2], ti_img.calc_data)

    def test_8ci(self):
        ti_img = TIPicture.open("tests/data/var/Pic1.8ci")
        ti_img.clear_white()

        arr = np.asarray(ti_img.array(), dtype=np.uint8)
        img = Image.open("tests/data/var/Pic1.8ci")

        self.assertEqual((np.asarray(Image.fromarray(arr)) == np.asarray(img)).all(), True)

        img.save(buf := io.BytesIO(), "8ci")
        buf.seek(0)

        self.assertEqual(buf.read()[72:-2], ti_img.calc_data)

    def test_8ca(self):
        ti_img = TIImage.open("tests/data/var/Image1.8ca")

        arr = np.asarray(ti_img.array(), dtype=np.uint8)
        img = Image.open("tests/data/var/Image1.8ca")

        self.assertEqual((np.asarray(Image.fromarray(arr)) == np.asarray(img)).all(), True)
