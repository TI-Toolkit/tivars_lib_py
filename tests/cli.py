import contextlib
import io
import shutil
import unittest

from tivars import *
from tivars.cli import *


def clean(directory):
    def outer(func):
        def inner(self):
            shutil.rmtree(directory, ignore_errors=True)
            func(self)
            shutil.rmtree(directory)

        return inner

    return outer


class CLITests(unittest.TestCase):
    def test_info(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli("info", "tests/data/var/Program.8xp")
            self.assertEqual(out.getvalue(),
                             "Header Information\n"
                                    "  Product ID  0x0a\n"
                                    "  Model       TI-84+ or newer\n"
                                    "  Comment     Created by TI Connect CE 5.1.0.68\n"
                                    "\n"
                                    "Entry Information\n"
                                    "  Type           TIProgram (ID 0x05)\n"
                                    "  Name           SETDATE\n"
                                    "  Version        0x04\n"
                                    "  Archived?      False\n"
                                    "\n"
                                    "  Data Length    5\n"
                                    "  Compatibility  TI-84+ (OS 0.01) or newer\n"
                                    "  Data           0300 ef00 31\n"
                                    "\n"
                                    "Program Information\n"
                                    "  Length  3\n"
                                    "  Lines   1\n"
                                    "\n"
                                    "  Program setDate(1\n\n\n")

    @clean("tests/cli")
    def test_bundle_round_trip(self):
        cli("unpack", "tests/data/var/TI83CEBundle_5.4.0.34.b83", outdir="tests/cli")
        cli("pack", "tests/cli", format="bundle", model=TI_83PCE, name="tests/cli/test_bundle")

        orig = TIBundle.open("tests/data/var/TI83CEBundle_5.4.0.34.b83")
        new = TIBundle.open("tests/cli/test_bundle.b83")

        self.assertListEqual(orig.unbundle(), new.unbundle())

    @clean("tests/cli")
    def test_group_round_trip(self):
        cli("unpack", "tests/data/var/Group.8xg", outdir="tests/cli")
        cli("pack", "tests/cli", outfile="tests/cli/test_group.8xg")

        orig = TIGroup.open("tests/data/var/Group.8xg")
        new = TIGroup.open("tests/cli/test_group.8xg")

        self.assertListEqual(orig.ungroup(), new.ungroup())
