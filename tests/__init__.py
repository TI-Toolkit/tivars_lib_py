import decimal
import unittest

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

        self.assertEqual(test_var.entries[0].meta,
                         test_var.entries[0].raw.data_length + test_var.entries[0].raw.type_id +
                         test_var.entries[0].raw.name + test_var.entries[0].raw.version +
                         test_var.entries[0].raw.archived)

        self.assertEqual(test_var.entries[0].raw.data, bytearray(b'\x03\x00\xef\x001'))
        self.assertEqual(test_var.entries[0].bytes(),
                         test_var.entries[0].raw.meta_length + test_var.entries[0].raw.meta +
                         test_var.entries[0].raw.data_length + test_var.entries[0].raw.data)

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
        test_program = TIProgram(name="SETDATE")
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
        self.assertEqual(test_real.mantissa, 42133700000000)
        self.assertEqual(test_real.is_undefined, False)
        self.assertEqual(test_real.is_complex_component, False)

        self.assertEqual(str(test_real), "-42.1337")
        self.assertEqual(test_real.decimal(), decimal.Decimal("-42.1337"))

        test_real.clear()
        test_real.load_string(string := "-42.1337")
        self.assertEqual(test_real.string(), string)

        with open("tests/data/Real.8xn", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_real.bytes(), file.read()[:-2])

    def test_complex_number(self):
        test_complex = TIComplex()
        test_complex.open("tests/data/Complex.8xc")

        self.assertEqual(test_complex.real.sign, -1)
        self.assertEqual(test_complex.real.exponent, 128)
        self.assertEqual(test_complex.real.mantissa, 50000000000000)

        self.assertEqual(test_complex.imag.sign, 1)
        self.assertEqual(test_complex.imag.exponent, 128)
        self.assertEqual(test_complex.imag.mantissa, 20000000000000)

        self.assertEqual(str(test_complex), "-5 + 2[i]")

        test_components = TIComplex(name="C")
        test_components.real, test_components.imag = test_complex.real, test_complex.imag
        self.assertEqual(test_complex.bytes(), test_components.bytes())

        test_complex.clear()
        test_complex.load_string(string := "-5 + 2[i]")
        self.assertEqual(test_complex.string(), string)

        with open("tests/data/Complex.8xc", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_complex.bytes(), file.read()[:-2])

    def test_real_list(self):
        test_real_list = TIRealList()
        test_real_list.open("tests/data/RealList.8xl")

        test_list = [TIReal("-1.0", name=test_real_list.name),
                     TIReal("2.0", name=test_real_list.name),
                     TIReal("999", name=test_real_list.name)]

        self.assertEqual(test_real_list.length, 3)
        self.assertEqual(test_real_list.list(), test_list)
        self.assertEqual(str(test_real_list), "[-1, 2, 999]")

    def test_complex_list(self):
        test_comp_list = TIComplexList()
        test_comp_list.open("tests/data/ComplexList.8xl")

        test_list = [TIComplex("1 + i", name=test_comp_list.name),
                     TIComplex("-3 + 2i", name=test_comp_list.name),
                     TIComplex("4", name=test_comp_list.name)]

        self.assertEqual(test_comp_list.length, 3)
        self.assertEqual(test_comp_list.list(), test_list)
        self.assertEqual(str(test_comp_list), "[1 + 1[i], -3 + 2[i], 4]")


class WindowTests(unittest.TestCase):
    def test_window(self):
        test_window = TIWindowSettings()
        test_window.open("tests/data/Window.8xw")

        zero, one = TIReal("0", name="WINDOW"), TIReal("1", name="WINDOW")
        undef = TIReal("1", name="WINDOW", flags=14)
        tau, pi_twelfths = TIReal("6.283185307", name="WINDOW"), TIReal("0.13089969389957", name="WINDOW")

        self.assertEqual(test_window.PlotStart, one)
        self.assertEqual(test_window.PlotStep, one)

        self.assertEqual(test_window.Thetamax, tau)
        self.assertEqual(test_window.Thetamin, zero)
        self.assertEqual(test_window.Thetastep, pi_twelfths)

        self.assertEqual(test_window.Tmax, tau)
        self.assertEqual(test_window.Tmin, zero)
        self.assertEqual(test_window.Tstep, pi_twelfths)

        self.assertEqual(test_window.unMin0, undef)
        self.assertEqual(test_window.unMin1, undef)
        self.assertEqual(test_window.vnMin0, undef)
        self.assertEqual(test_window.vnMin1, undef)
        self.assertEqual(test_window.wnMin0, undef)
        self.assertEqual(test_window.wnMin1, undef)

        self.assertEqual(test_window.Xmax, TIReal("10", name="WINDOW"))
        self.assertEqual(test_window.Xmin, TIReal("-10", name="WINDOW"))
        self.assertEqual(test_window.Xres, TIReal("2", name="WINDOW"))
        self.assertEqual(test_window.Xscl, TIReal("1", name="WINDOW"))

        self.assertEqual(test_window.Ymax, TIReal("20", name="WINDOW"))
        self.assertEqual(test_window.Ymin, TIReal("-20", name="WINDOW"))
        self.assertEqual(test_window.Yscl, TIReal("2", name="WINDOW"))

    def test_recall(self):
        test_recall = TIRecallWindow()
        test_recall.open("tests/data/RecallWindow.8xz")

        zero, one = TIReal("0", name="RCLWINDW"), TIReal("1", name="RCLWINDW")
        undef = TIReal("1", name="RCLWINDW", flags=14)
        tau, pi_twelfths = TIReal("6.283185307", name="RCLWINDW"), TIReal("0.13089969389957", name="RCLWINDW")

        self.assertEqual(test_recall.PlotStart, one)
        self.assertEqual(test_recall.PlotStep, one)

        self.assertEqual(test_recall.Thetamax, tau)
        self.assertEqual(test_recall.Thetamin, zero)
        self.assertEqual(test_recall.Thetastep, pi_twelfths)

        self.assertEqual(test_recall.Tmax, tau)
        self.assertEqual(test_recall.Tmin, zero)
        self.assertEqual(test_recall.Tstep, pi_twelfths)

        self.assertEqual(test_recall.unMin0, undef)
        self.assertEqual(test_recall.unMin1, undef)
        self.assertEqual(test_recall.vnMin0, undef)
        self.assertEqual(test_recall.vnMin1, undef)
        self.assertEqual(test_recall.wnMin0, undef)
        self.assertEqual(test_recall.wnMin1, undef)

        self.assertEqual(test_recall.Xmax, TIReal("10", name="RCLWINDW"))
        self.assertEqual(test_recall.Xmin, TIReal("-10", name="RCLWINDW"))
        self.assertEqual(test_recall.Xres, TIReal("1", name="RCLWINDW"))
        self.assertEqual(test_recall.Xscl, TIReal("1", name="RCLWINDW"))

        self.assertEqual(test_recall.Ymax, TIReal("10", name="RCLWINDW"))
        self.assertEqual(test_recall.Ymin, TIReal("-10", name="RCLWINDW"))
        self.assertEqual(test_recall.Yscl, TIReal("1", name="RCLWINDW"))
