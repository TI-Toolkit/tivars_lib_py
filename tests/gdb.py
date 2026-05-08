import json
import unittest

from tivars.types import *


class GDBTests(unittest.TestCase):
    def test_func_gdb(self):
        test_gdb = TIMonoGDB.open("tests/data/var/GraphDataBase.8xd")

        self.assertEqual(type(test_gdb), TIFuncGDB)
        self.assertEqual(test_gdb.name, "GDB1")

        self.assertEqual(test_gdb.Xmax, eleven_pi_over_four := TIReal("8.639379797"))
        self.assertEqual(test_gdb.Xmin, -eleven_pi_over_four)
        self.assertEqual(test_gdb.Xres, TIReal(2))
        self.assertEqual(test_gdb.Xscl, TIReal("1.5707963267949"))

        self.assertEqual(test_gdb.Ymax, TIReal(4.0))
        self.assertEqual(test_gdb.Ymin, TIReal(-4.0))
        self.assertEqual(test_gdb.Yscl, TIReal(1))

        self.assertEqual(test_gdb.Y1.equation(), TIEquation("sin(X", name="Y1"))
        self.assertEqual(test_gdb.Y1.style, GraphStyle.ThickLine)
        self.assertEqual(test_gdb.Y1.color, GraphColor.Blue)
        self.assertEqual(test_gdb.grid_color, GraphColor.MedGray)

        self.assertEqual(test_gdb.Y1.is_defined, True)
        self.assertEqual(test_gdb.Y2.is_defined, False)

        self.assertIn(GraphMode.Connected, test_gdb.mode_flags)
        self.assertIn(GraphMode.AxesOn, test_gdb.mode_flags)
        self.assertIn(GraphMode.ExprOn, test_gdb.extended_mode_flags)
        self.assertIn(GraphMode.DetectAsymptotesOn, test_gdb.color_mode_flags)

    def test_json(self):
        test_gdb = TIParamGDB()

        with open("tests/data/json/param.json") as file:
            param = json.load(file)

        test_gdb.load_dict(param)

        tau, pi_twenty_fourths = TIReal(6.283185307), TIReal("0.13089969389957")
        self.assertEqual(test_gdb.Xmax.bytes(), TIReal(10).bytes())
        self.assertEqual(test_gdb.Xmin, TIReal(-10))
        self.assertEqual(test_gdb.Tmax, tau)
        self.assertEqual(test_gdb.Tstep, pi_twenty_fourths)

        self.assertEqual(test_gdb.X2T.equation(), TIEquation(name="X2T"))
        self.assertEqual(test_gdb.X2T.style, GraphStyle.ThickLine)
        self.assertEqual(test_gdb.X2T.color, GraphColor.Red)
        self.assertEqual(test_gdb.axes_color, GraphColor.Black)

        self.assertIn(GraphMode.Sequential, test_gdb.mode_flags)
        self.assertIn(GraphMode.CoordOn, test_gdb.mode_flags)
        self.assertIn(GraphMode.ExprOn, test_gdb.extended_mode_flags)
        self.assertIn(GraphMode.DetectAsymptotesOn, test_gdb.color_mode_flags)

        self.assertEqual(test_gdb.dict(), param)
        self.assertEqual(dict(test_gdb), param)

        self.assertEqual(test_gdb.length, 142)
