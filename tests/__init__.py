import unittest

from tivars.models import *
from tivars.types import *
from tivars import TIHeader, TIVar


class VarTests(unittest.TestCase):
    def test_all_attributes(self):
        test_var = TIVar()
        test_var.open("tests/data/Program.8xp")

        self.assertEqual(test_var.header.magic, "**TI83F*")
        self.assertEqual(test_var.header.extra, b'\x1A\x0A')
        self.assertEqual(test_var.header.product_id, b'\x0A')
        self.assertEqual(test_var.header.comment, "Created by TI Connect CE 5.1.0.68")

        self.assertEqual(test_var.entries[0].meta_length, TIEntry.flash_meta_length)
        self.assertEqual(test_var.entries[0].name, "SETDATE")
        self.assertEqual(test_var.entries[0].version, b'\x04')
        self.assertEqual(test_var.entries[0].archived, False)

        self.assertEqual(str(test_var.entries[0]), "setDate(1")
        self.assertEqual(test_var.checksum, b'M\x03')

    def test_all_byte_sections(self):
        test_var = TIVar()
        test_var.open("tests/data/Program.8xp")

        self.assertEqual(test_var.header.raw.magic, b'**TI83F*')
        self.assertEqual(test_var.header.raw.extra, b'\x1A\x0A')
        self.assertEqual(test_var.header.raw.product_id, b'\x0A')
        self.assertEqual(test_var.header.raw.comment, b'Created by TI Connect CE 5.1.0.68'.ljust(42, b'\x00'))

        self.assertEqual(test_var.header.bytes(),
                         test_var.header.raw.magic + test_var.header.raw.extra +
                         test_var.header.raw.product_id + test_var.header.raw.comment)

        self.assertEqual(test_var.entries[0].raw.meta_length, b'\x0D\x00')
        self.assertEqual(test_var.entries[0].raw.name, b'SETDATE\x00')
        self.assertEqual(test_var.entries[0].raw.version, b'\x04')
        self.assertEqual(test_var.entries[0].raw.archived, b'\x00')

        self.assertEqual(test_var.entries[0].flash_bytes,
                         test_var.entries[0].raw.version + test_var.entries[0].raw.archived)

        self.assertEqual(test_var.entries[0].raw.data, bytearray(b'\x03\x00\xef\x001'))
        self.assertEqual(test_var.entries[0].bytes(),
                         test_var.entries[0].raw.meta_length + test_var.entries[0].raw.data_length +
                         test_var.entries[0].raw.type_id +
                         test_var.entries[0].raw.name + test_var.entries[0].raw.version +
                         test_var.entries[0].raw.archived + test_var.entries[0].raw.data_length +
                         test_var.entries[0].raw.data)

        self.assertEqual(test_var.checksum, b'M\x03')

    def test_multiple_entries(self):
        clibs = TIVar()
        clibs.open("tests/data/clibs.8xg")

        self.assertEqual(len(clibs.entries), 9)
        self.assertTrue(all(entry.type_id == b'\x15' for entry in clibs.entries))

        second = TIEntry()
        with open("tests/data/clibs.8xg", 'rb') as file:
            second.load_from_file(file, offset=1)

        self.assertEqual(second, clibs.entries[1])

    def test_save_to_file(self):
        test_var = TIVar()
        test_var.open("tests/data/Program.8xp")

        self.assertEqual(test_var.extension, "8xp")
        test_var.save("tests/data/Program_new.8xp")

        with open("tests/data/Program.8xp", 'rb') as orig:
            with open("tests/data/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())

    def test_truthiness(self):
        test_var = TIVar()
        self.assertEqual(bool(test_var), False)

        test_var.open("tests/data/clibs.8xg")
        self.assertEqual(bool(test_var), True)

        test_var.clear()
        self.assertEqual(bool(test_var), False)


class EntryTests(unittest.TestCase):
    def test_save_to_file(self):
        test_program = TIProgram()
        test_header = TIHeader()

        test_program.open("tests/data/Program.8xp")
        test_header.open("tests/data/Program.8xp")

        self.assertEqual(test_program.extension, "8xp")
        test_program.save("tests/data/Program_new.8xp", header=test_header)

        with open("tests/data/Program.8xp", 'rb') as orig:
            with open("tests/data/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())

    def test_form_vars(self):
        test_program = TIProgram()
        test_header = TIHeader()
        test_var = TIVar()

        with open("tests/data/Program.8xp", 'rb') as file:
            test_program.load_from_file(file)
            file.seek(0)

            test_header.load_from_file(file)
            file.seek(0)

            test_var.load_var_file(file)
            self.assertEqual(test_header | [test_program], test_var)

    def test_truthiness(self):
        test_program = TIEntry()
        self.assertEqual(bool(test_program), False)

        test_program.open("tests/data/Program.8xp")
        self.assertEqual(bool(test_program), True)

        test_program.clear()
        self.assertEqual(bool(test_program), False)


class TokenizationTests(unittest.TestCase):
    def test_load_from_file(self):
        test_var = TIVar()
        test_var.open("tests/data/Program.8xp")

        test_program = TIProgram()
        test_program.open("tests/data/Program.8xp")

        self.assertEqual(test_program, test_var.entries[0])

        del test_program
        test_program = TIProgram()

        with open("tests/data/Program.8xp", 'rb') as file:
            test_program.load_from_file(file)

            file.seek(55)
            self.assertEqual(test_program.bytes(), file.read()[:-2])

        self.assertEqual(test_program, test_var.entries[0])

    def test_load_from_string(self):
        test_program = TIProgram(name="SETDATE", model=TI_84P)
        test_program.comment = "Created by TI Connect CE 5.1.0.68"

        test_program.load_string(string := "setDate(1")
        self.assertEqual(test_program.string(), string)

        # Version is wrong(?)
        test_program.version = b'\x04'

        with open("tests/data/Program.8xp", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_program.bytes(), file.read()[:-2])

    def test_all_tokens(self):
        test_program = TIProgram()

        with open("tests/data/ALLTOKS.8Xp", 'rb') as file:
            test_program.load_from_file(file)
            file.seek(55)

            self.assertEqual(test_program.bytes(), file.read()[:-2])
            self.assertEqual(test_program.is_protected, False)


class NumericTests(unittest.TestCase):
    def test_real_number(self):
        test_real = TIReal()
        test_real.open("tests/data/Real.8xn")

        self.assertEqual(test_real.sign, -1)
        self.assertEqual(test_real.exponent, 129)
        self.assertEqual(test_real.mantissa, 4213370000000000)
        self.assertEqual(test_real.is_undefined, False)
        self.assertEqual(test_real.is_complex_component, False)

        self.assertEqual(str(test_real), "-42.1337")

        test_real.clear()
        test_real.load_string(string := "-42.1337")
        self.assertEqual(test_real.string(), string)

        with open("tests/data/Real.8xn", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_real.bytes(), file.read()[:-2])
