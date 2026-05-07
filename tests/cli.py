import contextlib
import io
import json
import os
import shutil
import unittest

from pathlib import Path
from tempfile import TemporaryDirectory

from tivars.bundle import *
from tivars.cli import *
from tivars.models import *
from tivars.types import *


# I really shouldn't have to write this myself
def in_clean_dir(func):
    def inner(self):
        with TemporaryDirectory() as tmp:
            shutil.copytree("tests", tmp, dirs_exist_ok=True)

            try:
                with contextlib.chdir(tmp):
                    os.makedirs("cli")
                    with contextlib.chdir("cli"):
                        func(self)

            except AttributeError:
                raise unittest.SkipTest("contextlib.chdir is not present in 3.10")

    return inner


class CLITests(unittest.TestCase):
    @in_clean_dir
    def test_convert_json(self):
        cli("convert", "../data/json/param.json", format="TIGDB", name="test_gdb")

        self.assertEqual(TIGDB.open("test_gdb.8xd").json(), json.load(file := open("../data/json/param.json")))
        file.close()

    @in_clean_dir
    def test_convert_number(self):
        cli("convert", "../data/var/Complex.8xc", format="text")
        self.assertEqual(Path("C.txt").read_text(), "-5 + 2i")

    @in_clean_dir
    def test_convert_picture(self):
        cli("convert", "../data/var/Pic1.8ci", outfile="test.png")
        cli("convert", "test.png", format="TIPicture")

        img = TIPicture.open("../data/var/Pic1.8ci")
        img.clear_white()

        self.assertEqual(img.data, TIPicture.open("test.8ci").data)

    @in_clean_dir
    def test_convert_program(self):
        cli("convert", "../data/var/Program.8xp", format="text")
        self.assertEqual(Path("SETDATE.txt").read_text(), "setDate(1")

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

    @in_clean_dir
    def test_bundle_round_trip(self):
        cli("unpack", "../data/var/TI83CEBundle_5.4.0.34.b83")
        cli("pack", ".", format="bundle", model=TI_83PCE, name="test_bundle")

        orig = TIBundle.open("../data/var/TI83CEBundle_5.4.0.34.b83")
        new = TIBundle.open("test_bundle.b83")

        self.assertCountEqual(orig.unbundle(), new.unbundle())

    @in_clean_dir
    def test_group_round_trip(self):
        cli("unpack", "../data/var/Group.8xg")
        cli("pack", ".", outfile="test_group.8xg")

        orig = TIGroup.open("../data/var/Group.8xg")
        new = TIGroup.open("test_group.8xg")

        self.assertCountEqual(orig.ungroup(), new.ungroup())
