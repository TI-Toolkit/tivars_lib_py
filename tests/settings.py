import unittest

from tivars.types import *


class SettingsTests(unittest.TestCase):
    def test_window(self):
        test_window = TIWindowSettings.open("tests/data/var/Window.8xw")

        zero, one, undef = TIReal(0), TIReal(1), TIUndefinedReal(1)
        tau, pi_twenty_fourths = TIReal("6.283185307"), TIReal("0.13089969389957")

        self.assertEqual(test_window.name, "Window")
        self.assertEqual(test_window.PlotStart, one)
        self.assertEqual(test_window.PlotStep, one)

        self.assertEqual(test_window.unMin0, undef)
        self.assertEqual(test_window.unMin1, undef)
        self.assertEqual(test_window.vnMin0, undef)
        self.assertEqual(test_window.vnMin1, undef)
        self.assertEqual(test_window.wnMin0, undef)
        self.assertEqual(test_window.wnMin1, undef)

        self.assertEqual(test_window.Thetamax, tau)
        self.assertEqual(test_window.Thetamin, zero)
        self.assertEqual(test_window.Thetastep, pi_twenty_fourths)

        self.assertEqual(test_window.Tmax, tau)
        self.assertEqual(test_window.Tmin, zero)
        self.assertEqual(test_window.Tstep, pi_twenty_fourths)

        self.assertEqual(test_window.Xmax, TIReal("10"))
        self.assertEqual(test_window.Xmin, TIReal("-10"))
        self.assertEqual(test_window.Xres, TIReal(2))
        self.assertEqual(test_window.Xscl, TIReal("1"))

        self.assertEqual(test_window.Ymax, TIReal("20"))
        self.assertEqual(test_window.Ymin, TIReal(-20))
        self.assertEqual(test_window.Yscl, TIReal("2"))

    def test_recall(self):
        test_recall = TIRecallWindow.open("tests/data/var/RecallWindow.8xz")

        zero, one, undef = TIReal("0"), TIReal("1"), TIUndefinedReal("1")
        tau, pi_twenty_fourths = TIReal(6.283185307), TIReal("0.13089969389957")

        self.assertEqual(test_recall.name, "RclWindw")
        self.assertEqual(test_recall.PlotStart, one)
        self.assertEqual(test_recall.PlotStep, one)

        self.assertEqual(test_recall.unMin0, undef)
        self.assertEqual(test_recall.unMin1, undef)
        self.assertEqual(test_recall.vnMin0, undef)
        self.assertEqual(test_recall.vnMin1, undef)
        self.assertEqual(test_recall.wnMin0, undef)
        self.assertEqual(test_recall.wnMin1, undef)

        self.assertEqual(test_recall.Thetamax, tau)
        self.assertEqual(test_recall.Thetamin, zero)
        self.assertEqual(test_recall.Thetastep, pi_twenty_fourths)

        self.assertEqual(test_recall.Tmax, tau)
        self.assertEqual(test_recall.Tmin, zero)
        self.assertEqual(test_recall.Tstep, pi_twenty_fourths)

        self.assertEqual(test_recall.Xmax, TIReal("10"))
        self.assertEqual(test_recall.Xmin, TIReal(-10.0))
        self.assertEqual(test_recall.Xres, TIReal("1"))
        self.assertEqual(test_recall.Xscl, TIReal("1"))

        self.assertEqual(test_recall.Ymax, TIReal("10"))
        self.assertEqual(test_recall.Ymin, TIReal("-10"))
        self.assertEqual(test_recall.Yscl, TIReal(1))

    def test_table(self):
        test_table = TITableSettings.open("tests/data/var/TableRange.8xt")

        self.assertEqual(test_table.name, "TblSet")
        self.assertEqual(test_table.TblMin, TIReal(0.0))
        self.assertEqual(test_table.DeltaTbl, TIReal("1"))
