import decimal
import json
import unittest

from tivars.types import *
from tivars import TIHeader, TIVar


class VarTests(unittest.TestCase):
    def test_all_attributes(self):
        test_var = TIVar()
        test_var.open("tests/data/var/Program.8xp")

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
        test_var.open("tests/data/var/Program.8xp")

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
        clibs.open("tests/data/var/clibs.8xg")

        self.assertEqual(len(clibs.entries), 9)
        self.assertTrue(all(entry.type_id == b'\x15' for entry in clibs.entries))

        second = TIEntry()
        with open("tests/data/var/clibs.8xg", 'rb') as file:
            second.load_from_file(file, offset=1)

        self.assertEqual(second, clibs.entries[1])

    def test_save_to_file(self):
        test_var = TIVar()
        test_var.open("tests/data/var/Program.8xp")

        self.assertEqual(test_var.extension, "8xp")
        test_var.save("tests/data/var/Program_new.8xp")

        with open("tests/data/var/Program.8xp", 'rb') as orig:
            with open("tests/data/var/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())

    def test_truthiness(self):
        test_var = TIVar()
        self.assertEqual(bool(test_var), False)

        test_var.open("tests/data/var/clibs.8xg")
        self.assertEqual(bool(test_var), True)

        test_var.clear()
        self.assertEqual(bool(test_var), False)


class EntryTests(unittest.TestCase):
    def test_save_to_file(self):
        test_program = TIProgram()
        test_header = TIHeader()

        test_program.open("tests/data/var/Program.8xp")
        test_header.open("tests/data/var/Program.8xp")

        test_program.save("tests/data/var/Program_new.8xp", header=test_header)

        with open("tests/data/var/Program.8xp", 'rb') as orig:
            with open("tests/data/var/Program_new.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())

    def test_form_vars(self):
        test_program = TIProgram()
        test_header = TIHeader()
        test_var = TIVar()

        with open("tests/data/var/Program.8xp", 'rb') as file:
            test_program.load_from_file(file)
            file.seek(0)

            test_header.load_from_file(file)
            file.seek(0)

            test_var.load_var_file(file)
            self.assertEqual(test_header | [test_program], test_var)

    def test_truthiness(self):
        test_program = TIEntry()
        self.assertEqual(bool(test_program), False)

        test_program.open("tests/data/var/Program.8xp")
        self.assertEqual(bool(test_program), True)


class TokenizationTests(unittest.TestCase):
    def test_load_from_file(self):
        test_var = TIVar()
        test_var.open("tests/data/var/Program.8xp")

        test_program = TIProgram()
        test_program.open("tests/data/var/Program.8xp")

        self.assertEqual(test_program, test_var.entries[0])

        del test_program
        test_program = TIProgram()

        with open("tests/data/var/Program.8xp", 'rb') as file:
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

        with open("tests/data/var/Program.8xp", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_program.bytes(), file.read()[:-2])

    def test_all_tokens(self):
        test_program = TIProgram()

        with open("tests/data/var/ALLTOKS.8Xp", 'rb') as file:
            test_program.load_from_file(file)
            file.seek(55)

            self.assertEqual(test_program.bytes(), file.read()[:-2])
            self.assertEqual(test_program.is_protected, False)


class NumericTests(unittest.TestCase):
    def test_real_number(self):
        test_real = TIReal()
        test_real.open("tests/data/var/Real.8xn")

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

        with open("tests/data/var/Real.8xn", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_real.bytes(), file.read()[:-2])

    def test_complex_number(self):
        test_complex = TIComplex()
        test_complex.open("tests/data/var/Complex.8xc")

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

        with open("tests/data/var/Complex.8xc", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_complex.bytes(), file.read()[:-2])

    def test_real_list(self):
        test_real_list = TIRealList()
        test_real_list.open("tests/data/var/RealList.8xl")

        test_list = [TIReal("-1.0"), TIReal("2.0"), TIReal("999")]

        self.assertEqual(test_real_list.length, 3)
        self.assertEqual(test_real_list.list(), test_list)
        self.assertEqual(list(iter(test_real_list)), test_list)
        self.assertEqual(str(test_real_list), "[-1, 2, 999]")

    def test_complex_list(self):
        test_comp_list = TIComplexList()
        test_comp_list.open("tests/data/var/ComplexList.8xl")

        test_list = [TIComplex(1 + 1j), TIComplex("-3 + 2i"), TIComplex(4 + 0j)]

        self.assertEqual(test_comp_list.length, 3)
        self.assertEqual(test_comp_list.list(), test_list)
        self.assertEqual(list(iter(test_comp_list)), test_list)
        self.assertEqual(str(test_comp_list), "[1 + 1[i], -3 + 2[i], 4]")

    def test_matrix(self):
        test_matrix = TIMatrix()
        test_matrix.open("tests/data/var/Matrix_3x3_standard.8xm")

        test_array = [[TIReal(0.5), TIReal(-1.0), TIReal("2.6457513110646")],
                      [TIReal("2.7386127875258"), TIReal("0.5"), TIReal("3.1415926535898")],
                      [TIReal("1"), TIReal(99999999), TIReal(0)]]

        self.assertEqual(test_matrix.height, 3)
        self.assertEqual(test_matrix.width, 3)
        self.assertEqual(test_matrix.matrix(), test_array)
        self.assertEqual(list(iter(test_matrix)), [entry for row in test_array for entry in row])

        self.assertEqual(str(test_matrix), "[[0.5, -1, 2.6457513110646],"
                                           " [2.7386127875258, 0.5, 3.1415926535898],"
                                           " [1, 99999999, 0]]")


class SettingsTests(unittest.TestCase):
    def test_window(self):
        test_window = TIWindowSettings()
        test_window.open("tests/data/var/Window.8xw")

        zero, one, undef = TIReal(0), TIReal(1), TIReal(1, flags={1: 1, 2: 1, 3: 1})
        tau, pi_twenty_fourths = TIReal("6.283185307"), TIReal("0.13089969389957")

        self.assertEqual(test_window.PlotStart, one)
        self.assertEqual(test_window.PlotStep, one)

        self.assertEqual(test_window.Thetamax, tau)
        self.assertEqual(test_window.Thetamin, zero)
        self.assertEqual(test_window.Thetastep, pi_twenty_fourths)

        self.assertEqual(test_window.Tmax, tau)
        self.assertEqual(test_window.Tmin, zero)
        self.assertEqual(test_window.Tstep, pi_twenty_fourths)

        self.assertEqual(test_window.unMin0, undef)
        self.assertEqual(test_window.unMin1, undef)
        self.assertEqual(test_window.vnMin0, undef)
        self.assertEqual(test_window.vnMin1, undef)
        self.assertEqual(test_window.wnMin0, undef)
        self.assertEqual(test_window.wnMin1, undef)

        self.assertEqual(test_window.Xmax, TIReal("10"))
        self.assertEqual(test_window.Xmin, TIReal("-10"))
        self.assertEqual(test_window.Xres, TIReal(2))
        self.assertEqual(test_window.Xscl, TIReal("1"))

        self.assertEqual(test_window.Ymax, TIReal("20"))
        self.assertEqual(test_window.Ymin, TIReal(-20))
        self.assertEqual(test_window.Yscl, TIReal("2"))

    def test_recall(self):
        test_recall = TIRecallWindow()
        test_recall.open("tests/data/var/RecallWindow.8xz")

        zero, one, undef = TIReal("0"), TIReal("1"), TIReal("1", flags={1: 1, 2: 1, 3: 1})
        tau, pi_twenty_fourths = TIReal(6.283185307), TIReal("0.13089969389957")

        self.assertEqual(test_recall.PlotStart, one)
        self.assertEqual(test_recall.PlotStep, one)

        self.assertEqual(test_recall.Thetamax, tau)
        self.assertEqual(test_recall.Thetamin, zero)
        self.assertEqual(test_recall.Thetastep, pi_twenty_fourths)

        self.assertEqual(test_recall.Tmax, tau)
        self.assertEqual(test_recall.Tmin, zero)
        self.assertEqual(test_recall.Tstep, pi_twenty_fourths)

        self.assertEqual(test_recall.unMin0, undef)
        self.assertEqual(test_recall.unMin1, undef)
        self.assertEqual(test_recall.vnMin0, undef)
        self.assertEqual(test_recall.vnMin1, undef)
        self.assertEqual(test_recall.wnMin0, undef)
        self.assertEqual(test_recall.wnMin1, undef)

        self.assertEqual(test_recall.Xmax, TIReal("10"))
        self.assertEqual(test_recall.Xmin, TIReal(-10.0))
        self.assertEqual(test_recall.Xres, TIReal("1"))
        self.assertEqual(test_recall.Xscl, TIReal("1"))

        self.assertEqual(test_recall.Ymax, TIReal("10"))
        self.assertEqual(test_recall.Ymin, TIReal("-10"))
        self.assertEqual(test_recall.Yscl, TIReal(1))

    def test_table(self):
        test_table = TITableSettings()
        test_table.open("tests/data/var/TableRange.8xt")

        self.assertEqual(test_table.TblMin, TIReal(0.0))
        self.assertEqual(test_table.DeltaTbl, TIReal("1"))


class GDBTests(unittest.TestCase):
    def test_func_gdb(self):
        test_gdb = TIMonoGDB()
        test_gdb.open("tests/data/var/GraphDataBase.8xd")

        self.assertEqual(type(test_gdb), TIFuncGDB)
        self.assertEqual(test_gdb.Xmax, eleven_pi_over_four := TIReal("8.639379797"))
        self.assertEqual(test_gdb.Xmin, -eleven_pi_over_four)
        self.assertEqual(test_gdb.Xres, TIReal(2))
        self.assertEqual(test_gdb.Xscl, TIReal("1.5707963267949"))

        self.assertEqual(test_gdb.Ymax, TIReal(4.0))
        self.assertEqual(test_gdb.Ymin, TIReal(-4.0))
        self.assertEqual(test_gdb.Yscl, TIReal(1))

        self.assertEqual(test_gdb.Y1.equation(), TIEquation("sin(X"))
        self.assertEqual(test_gdb.Y1.style, GraphStyle.ThickLine)
        self.assertEqual(test_gdb.Y1.color, GraphColor.Blue)
        self.assertEqual(test_gdb.grid_color, GraphColor.MedGray)

        self.assertIn(GraphMode.Connected, test_gdb.mode_flags)
        self.assertIn(GraphMode.AxesOn, test_gdb.mode_flags)
        self.assertIn(GraphMode.ExprOn, test_gdb.extended_mode_flags)
        self.assertIn(GraphMode.DetectAsymptotesOff, test_gdb.color_mode_flags)

    def test_json(self):
        test_gdb = TIParamGDB()

        with open("tests/data/json/param.json") as file:
            param = json.load(file)

        test_gdb.load_dict(param)

        tau, pi_twenty_fourths = TIReal(6.283185307), TIReal("0.13089969389957")
        self.assertEqual(test_gdb.Xmax, TIReal(10))
        self.assertEqual(test_gdb.Xmin, TIReal(-10))
        self.assertEqual(test_gdb.Tmax, tau)
        self.assertEqual(test_gdb.Tstep, pi_twenty_fourths)

        self.assertEqual(test_gdb.X2T.equation(), TIEquation())
        self.assertEqual(test_gdb.X2T.style, GraphStyle.ThickLine)
        self.assertEqual(test_gdb.X2T.color, GraphColor.Red)
        self.assertEqual(test_gdb.axes_color, GraphColor.Black)

        self.assertIn(GraphMode.Sequential, test_gdb.mode_flags)
        self.assertIn(GraphMode.CoordOn, test_gdb.mode_flags)
        self.assertIn(GraphMode.ExprOn, test_gdb.extended_mode_flags)
        self.assertIn(GraphMode.DetectAsymptotesOn, test_gdb.color_mode_flags)

        self.assertEqual(test_gdb.dict(), param)
        self.assertEqual(dict(test_gdb), param)
