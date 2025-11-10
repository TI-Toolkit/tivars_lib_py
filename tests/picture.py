import unittest

from tivars.types import *


class PictureTests(unittest.TestCase):
    def test_mono_picture(self):
        test_picture = TIPicture()

        with open("tests/data/var/BartSimpson.8xi", 'rb') as file:
            test_picture.load_from_file(file)
            file.seek(0)

            self.assertEqual(test_picture.bytes(), file.read()[55:-2])

        self.assertEqual(test_picture.name, "Pic2")

        test_from_array = TIMonoPicture()
        test_from_array.load_array(test_picture.array())
        self.assertEqual(test_from_array.array(), test_picture.array())

    def test_picture(self):
        test_picture = TIPicture()

        with open("tests/data/var/Pic1.8ci", 'rb') as file:
            test_picture.load_from_file(file)
            file.seek(0)

            self.assertEqual(test_picture.bytes(), file.read()[55:-2])

        self.assertEqual(test_picture.name, "Pic1")

        test_from_array = TIPicture()
        test_from_array.load_array(test_picture.array())
        self.assertEqual(test_from_array.array(), test_picture.array())

    def test_image(self):
        test_image = TIImage()

        with open("tests/data/var/Image1.8ca", 'rb') as file:
            test_image.load_from_file(file)
            file.seek(0)

            self.assertEqual(test_image.bytes(), file.read()[55:-2])

        self.assertEqual(test_image.name, "Image1")

        test_from_array = TIImage()
        test_from_array.load_array(test_image.array())
        self.assertEqual(test_from_array.array(), test_image.array())
