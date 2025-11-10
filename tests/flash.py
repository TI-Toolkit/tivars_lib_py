import unittest

from tivars.types import *
from tivars import TIFlashHeader


class FlashTests(unittest.TestCase):
    def test_app(self):
        test_app = TIFlashHeader()

        with open("tests/data/var/smartpad.8xk", 'rb') as file:
            test_app.load_from_file(file)
            file.seek(0)

            self.assertEqual(test_app.bytes(), file.read())

        self.assertEqual(test_app.object_type, 0x88)
        self.assertEqual(test_app.device_type, DeviceType.TI_83P)
        self.assertEqual(test_app.product_id, 0x00)
        self.assertEqual(type(test_app), TIApp)

        self.assertEqual(test_app.binary_flag, 0x01)
        self.assertEqual(type(test_app.data), list)

    def test_os(self):
        test_os = TIFlashHeader.open("tests/data/var/TI-84_Plus_CE-Python-OS-5.8.0.0022.8eu")

        self.assertEqual(test_os.revision, "5.8")
        self.assertEqual(test_os.object_type, 0x00)
        self.assertEqual(test_os.product_id, 0x13)
        self.assertEqual(type(test_os), TIOperatingSystem)

        self.assertEqual(test_os.binary_flag, 0x00)
        self.assertEqual(type(test_os.data), bytes)

    def test_license(self):
        test_license = TILicense.open("tests/data/var/ti89_2.01_10-13-1999.89u")

        self.assertEqual(test_license.magic, "**TIFL**")
        self.assertEqual(test_license.date, (12, 10, 1999))
        self.assertEqual(test_license.devices, [(0x74, 0x3E), (0x73, 0x3E), (0x98, 0x3E), (0x88, 0x3E)])
        self.assertEqual(test_license.license.split("\r\n")[2], "Texas Instruments License Agreement")
