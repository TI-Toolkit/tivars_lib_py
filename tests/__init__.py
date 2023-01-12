import unittest

from tivars.models import *
from tivars.types import *


class VarTests(unittest.TestCase):
    def test_all_attributes(self):
        test_var = TIProgram()
        test_var.open("tests/data/Program.8xp")

        self.assertEqual(test_var.magic, "**TI83F*")
        self.assertEqual(test_var.extra, b'\x1A\x0A')
        self.assertEqual(test_var.product_id, b'\x0A')
        self.assertEqual(test_var.comment, "Created by TI Connect CE 5.1.0.68")

        self.assertEqual(test_var.meta_length, TIVar.flash_meta_length)
        self.assertEqual(test_var.name, "SETDATE")
        self.assertEqual(test_var.version, b'\x04')
        self.assertEqual(test_var.archived, False)

        self.assertEqual(test_var.header.entry_length, test_var.entry_length)


class TokenizationTests(unittest.TestCase):
    def test_load_from_file(self):
        test_program = TIProgram()
        test_program.open("tests/data/Program.8xp")

        with open("tests/data/Program.8xp", 'rb') as file:
            self.assertEqual(test_program.bytes(), file.read())
            file.seek(0)

            test_program.load(file)
            file.seek(0)
            self.assertEqual(test_program.bytes(), file.read())

    def test_load_from_string(self):
        test_program = TIProgram(name="SETDATE", model=TI_84P)
        test_program.comment = "Created by TI Connect CE 5.1.0.68"
        test_program.version = b'\x04'

        test_program.load_string(string := "setDate(1")

        with open("tests/data/Program.8xp", 'rb') as file:
            self.assertEqual(test_program.bytes(), file.read())
            self.assertEqual(test_program.string(), string)

    def test_all_tokens(self):
        test_program = TIProgram()

        with open("tests/data/ALLTOKS.8Xp", 'rb') as file:
            test_program.load(file)
            file.seek(0)

            self.assertEqual(test_program.bytes(), file.read())

    def test_save_to_file(self):
        test_program = TIProgram()

        test_program.open("tests/data/Program.8xp")
        test_program.save("tests/data/Program_new.8xp")

        with open("tests/data/Program.8xp", 'rb') as orig:
            with open("tests/data/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())
