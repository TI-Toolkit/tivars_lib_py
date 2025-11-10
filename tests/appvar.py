import unittest

from tivars.types import *


class AppVarTests(unittest.TestCase):
    def test_app_var(self):
        test_app_var = TIAppVar()

        with open("tests/data/var/AppVar.8xv", 'rb') as file:
            test_app_var.load_from_file(file)
            file.seek(0)

            self.assertEqual(test_app_var.bytes(), file.read()[55:-2])

        self.assertEqual(test_app_var.name, "FILEIOC")
        self.assertEqual(test_app_var.length, 2578)
