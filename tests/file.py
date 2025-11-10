import unittest

from tivars.models import *
from tivars.types import *
from tivars import TIHeader, TIVarFile, TIFlashFile, TIFile, TIBundle


class FileTests(unittest.TestCase):
    def test_file_coercion(self):
        test_var_file = TIFile.open("tests/data/var/ALLTOKS.8xp")
        test_flash_file = TIFile.open("tests/data/var/TI-84_Plus_CE-Python-OS-5.8.0.0022.8eu")
        test_bundle = TIFile.open("tests/data/var/TI84CEBundle_5.4.0.34.b84")

        self.assertEqual(type(test_var_file), TIVarFile)
        self.assertEqual(type(test_flash_file), TIFlashFile)
        self.assertEqual(type(test_bundle), TIBundle)

    def test_bundle(self):
        test_bundle = TIBundle()

        with open("tests/data/var/TI83CEBundle_5.4.0.34.b83", 'rb') as file:
            test_bundle.load_bytes(file.read())

            file.seek(0)
            self.assertEqual(test_bundle.bytes(), file.read())

        self.assertEqual(test_bundle.version, 1)
        self.assertEqual(test_bundle.target_type, "RESTORE")
        self.assertEqual(test_bundle.comment, "Created by TI Bundle Creation Tool 1.0.0.15")

        files = test_bundle.unbundle()
        self.assertEqual(len(files), 27)
        self.assertEqual(files[0].name, "BONJOUR")
        self.assertEqual(type(files[9].entries[0]), TIImage)

        self.assertEqual(files, test_bundle.bundle(files, model=TI_83PCE).unbundle())


class VarTests(unittest.TestCase):
    def test_all_attributes(self):
        test_var = TIVarFile.open("tests/data/var/Program.8xp")
        test_header = TIHeader.open("tests/data/var/Program.8xp")

        self.assertEqual(test_var.header, test_header)

        self.assertEqual(type(test_var.entries[0]), TIProgram)
        self.assertEqual(type(test_var.entries[0]).type_id, 0x05)

        self.assertEqual(test_var.entries[0].meta_length, TIEntry.flash_meta_length)
        self.assertEqual(test_var.entries[0].type_id, 0x05)
        self.assertEqual(test_var.entries[0].name, "SETDATE")
        self.assertEqual(test_var.entries[0].version, 0x04)
        self.assertEqual(test_var.entries[0].archived, False)

        self.assertEqual(str(test_var.entries[0]), "setDate(1")
        self.assertEqual(test_var.checksum, b'M\x03')

    def test_all_sections(self):
        test_var = TIVarFile.open("tests/data/var/Program.8xp")

        self.assertEqual(test_var.header.raw.magic, b'**TI83F*')
        self.assertEqual(test_var.header.raw.extra, b'\x1A\x0A')
        self.assertEqual(test_var.header.raw.product_id, b'\x0A')
        self.assertEqual(test_var.header.raw.comment, b'Created by TI Connect CE 5.1.0.68'.ljust(42, b'\x00'))

        self.assertEqual(test_var.header.bytes(),
                         test_var.header.raw.magic + test_var.header.raw.extra +
                         test_var.header.raw.product_id + test_var.header.raw.comment)

        self.assertEqual(test_var.entries[0].raw.meta_length, b'\x0D\x00')
        self.assertEqual(test_var.entries[0].raw.type_id, b'\x05')
        self.assertEqual(test_var.entries[0].raw.name, b'SETDATE\x00')
        self.assertEqual(test_var.entries[0].raw.version, b'\x04')
        self.assertEqual(test_var.entries[0].raw.archived, b'\x00')

        self.assertEqual(test_var.entries[0].flash_bytes,
                         test_var.entries[0].raw.version + test_var.entries[0].raw.archived)

        self.assertEqual(test_var.entries[0].meta,
                         test_var.entries[0].raw.calc_data_length + test_var.entries[0].raw.type_id +
                         test_var.entries[0].raw.name + test_var.entries[0].raw.version +
                         test_var.entries[0].raw.archived)

        self.assertEqual(test_var.entries[0].raw.calc_data, bytearray(b'\x03\x00\xef\x001'))
        self.assertEqual(test_var.entries[0].bytes(),
                         test_var.entries[0].raw.meta_length + test_var.entries[0].raw.meta +
                         test_var.entries[0].raw.calc_data_length + test_var.entries[0].raw.calc_data)

        self.assertEqual(test_var.checksum, b'M\x03')

    def test_multiple_entries(self):
        clibs = TIVarFile.open("tests/data/var/clibs.8xg")

        self.assertEqual(len(clibs.entries), 9)
        self.assertTrue(all(entry.type_id == 0x15 for entry in clibs.entries))

        with self.assertWarns(UserWarning):
            first = TIEntry.open("tests/data/var/clibs.8xg")

        with open("tests/data/var/clibs.8xg", 'rb') as file:
            second = TIEntry()
            second.load_from_file(file, offset=1)

        self.assertEqual(first, clibs.entries[0])
        self.assertEqual(second, clibs.entries[1])

    def test_save_to_file(self):
        test_var = TIVarFile.open("tests/data/var/Program.8xp")

        self.assertEqual(test_var.get_extension(), "8xp")
        self.assertEqual(test_var.get_filename(), "Program.8xp")
        test_var.save("tests/data/var/Program_new.8xp")

        with open("tests/data/var/Program.8xp", 'rb') as orig:
            with open("tests/data/var/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())

        self.assertEqual(test_var.supported_by(TI_84P), True)
        self.assertEqual(test_var.supported_by(TI_83), False)

    def test_truthiness(self):
        test_var = TIVarFile.open("tests/data/var/clibs.8xg")
        self.assertEqual(bool(test_var), True)

        test_var.clear()
        self.assertEqual(bool(test_var), False)


class EntryTests(unittest.TestCase):
    def test_save_to_file(self):
        test_program = TIEntry.open("tests/data/var/Program.8xp")
        test_header = TIHeader.open("tests/data/var/Program.8xp")

        test_program.save("tests/data/var/Program_new.8xp", header=test_header)

        self.assertEqual(test_program.export().get_filename(), "SETDATE.8xp")
        self.assertEqual(test_program.export().get_filename(model=TI_83), "SETDATE.83p")

        with open("tests/data/var/Program.8xp", 'rb') as orig:
            with open("tests/data/var/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())

    def test_form_vars(self):
        test_program = TIProgram()
        test_header = TIHeader()
        test_var = TIVarFile()

        with open("tests/data/var/Program.8xp", 'rb') as file:
            test_program.load_from_file(file)
            file.seek(0)

            test_header.load_from_file(file)
            file.seek(0)

            test_var.load_file(file)
            self.assertEqual(test_header | [test_program], test_var)

    def test_truthiness(self):
        test_program = TIEntry.open("tests/data/var/Program.8xp")
        self.assertEqual(bool(test_program), True)

        test_program.clear()
        self.assertEqual(bool(test_program), True)

    def test_hex(self):
        test_program = TIEntry.open("tests/data/var/Program.8xp")
        self.assertEqual(f"{test_program}", "setDate(1")
        self.assertEqual(f"{test_program:-2X:}", "0300:EF00:31")
