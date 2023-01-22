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
        self.assertEqual(test_var.version, 4)
        self.assertEqual(test_var.archived, False)

        self.assertEqual(str(test_var), "setDate(1")
        self.assertEqual(test_var.checksum, b'M\x03')

    def test_all_byte_sections(self):
        test_var = TIProgram()
        test_var.open("tests/data/Program.8xp")

        self.assertEqual(test_var[TIVar.magic], b'**TI83F*')
        self.assertEqual(test_var[TIVar.extra], b'\x1A\x0A')
        self.assertEqual(test_var[TIVar.product_id], b'\x0A')
        self.assertEqual(test_var[TIVar.comment], b'Created by TI Connect CE 5.1.0.68'.ljust(42, b'\x00'))

        self.assertEqual(test_var[TIVar.header], test_var[TIVar.magic] + test_var[TIVar.extra] +
                         test_var[TIVar.product_id] + test_var[TIVar.comment] + test_var[TIVar.entry_length])

        self.assertEqual(test_var["meta_length"], b'\x0D\x00')
        self.assertEqual(test_var["name"], b'SETDATE\x00')
        self.assertEqual(test_var["version"], b'\x04')
        self.assertEqual(test_var["archived"], b'\x00')

        self.assertEqual(test_var["data"], bytearray(b'\x03\x00\xef\x001'))
        self.assertEqual(test_var["entry"], test_var["meta_length"] + test_var["meta"] +
                         test_var["data_length"] + test_var["data"])

        self.assertEqual(test_var["checksum"], b'M\x03')

    def test_metadata_update(self):
        test_var = TIProgram()
        test_var.open("tests/data/Program.8xp")

        test_var[TIVar.entry_length] = b'iB'
        test_var["checksum"] = b'xD'

        with open("tests/data/Program.8xp", 'rb') as file:
            self.assertNotEqual(test_var, file.read())

            file.seek(0)
            self.assertEqual(test_var.bytes(), file.read())


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
        test_program.version = 4

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
