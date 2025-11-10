import unittest

from tivars.models import *
from tivars.tokenizer import *
from tivars.types import *
from tivars import TIVarFile


class ModelTests(unittest.TestCase):
    def test_all_models(self):
        for model in TIModel.MODELS:
            self.assertEqual(model, eval(model.name.translate({43: "P", 45: "_", 46: "_", 58: "_"})))

        self.assertEqual(TIModel.MODELS, sorted(TIModel.MODELS))


class TokenizationTests(unittest.TestCase):
    def test_load_from_file(self):
        test_var = TIVarFile.open("tests/data/var/Program.8xp")

        test_program = TIProgram.open("tests/data/var/Program.8xp")

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
        self.assertEqual(f"{test_program:a}", string)
        self.assertEqual(f"{test_program:02d: }", f"00: {string}")

        self.assertEqual(test_program.tokens(), [TI_84PCE.tokens["setDate("],
                                                 TI_84PCE.tokens[b'1']])

        # Version is wrong(?)
        test_program.version = 0x04

        with open("tests/data/var/Program.8xp", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_program.bytes(), file.read()[:-2])

        self.assertEqual(test_program.supported_by(TI_83PCE), True)
        self.assertEqual(test_program.supported_by(TI_83), False)

    def test_all_tokens(self):
        test_program = TIProgram()

        with open("tests/data/var/ALLTOKS.8Xp", 'rb') as file:
            test_program.load_from_file(file)
            file.seek(55)

            self.assertEqual(test_program.bytes(), file.read()[:-2])
            self.assertEqual(test_program.is_protected, False)
            self.assertEqual(test_program.is_tokenized, True)

    def test_protection(self):
        test_program = TIProtectedProgram(name="SETDATE")
        test_program.load_string("setDate(1")
        test_program.unprotect()

        test_program.version = 0x04
        with open("tests/data/var/Program.8xp", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_program.bytes(), file.read()[:-2])

    def test_assembly(self):
        test_program = TIProgram.open("tests/data/var/COLORZ.8xp")
        self.assertEqual(type(test_program), TIProtectedAsmProgram)

        self.assertEqual(TIProgram.decode(test_program.data[:26]), "Disp \"Needs Doors CSE\"")

        test_program = TIProgram.open("tests/data/var/ZLOAD.83P")
        self.assertEqual(type(test_program), TIAsmProgram)

        with self.assertWarns(UserWarning):
            self.assertEqual(test_program.string()[-12:], "End\n0000\nEnd")

    def test_modes(self):
        interpolation = "A and B:Disp \"A and B\":Send(\"SET SOUND eval(A and B) TIME 2"
        names = "Disp \"WHITE,ʟWHITE,prgmWHITE\",WHITE,ʟWHITE:prgmWHITE:prgmABCDEF"

        self.assertEqual(TIProgram.encode(interpolation, mode="max"),
                         b'A@B>\xde*A@B*>\xe7*SET)SOUND)\xef\x98A@B\x11)TIME)2')
        self.assertEqual(TIProgram.encode(interpolation, mode="smart"),
                         b'A@B>\xde*A)\xbb\xb0\xbb\xbe\xbb\xb3)B*>\xe7*SET)SOUND)\xef\x98A@B\x11)TIME)2')
        self.assertEqual(TIProgram.encode(interpolation, mode="string"),
                         b'A)\xbb\xb0\xbb\xbe\xbb\xb3)B>D\xbb\xb8\xbb\xc3\xbb\xc0)*A)\xbb\xb0'
                         b'\xbb\xbe\xbb\xb3)B*>S\xbb\xb4\xbb\xbe\xbb\xb3\x10*SET)SOUND)\xbb'
                         b'\xb4\xbb\xc6\xbb\xb0\xbb\xbc\x10A)\xbb\xb0\xbb\xbe\xbb\xb3)B\x11)TIME)2')

        self.assertEqual(TIProgram.encode(names, mode="max"),
                         b'\xde*\xefK+\xeb\xefK+_\xefK*+\xefK+\xeb\xefK>_\xefK>_ABCDEF')
        self.assertEqual(TIProgram.encode(names, mode="smart"),
                         b'\xde*WHITE+\xebWHITE+\xbb\xc0\xbb\xc2\xbb\xb6\xbb\xbdWHITE*+\xefK+\xebWHITE>_WHITE>_ABCDEF')
        self.assertEqual(TIProgram.encode(names, mode="string"),
                         b'D\xbb\xb8\xbb\xc3\xbb\xc0)*WHITE+\xebWHITE+\xbb\xc0\xbb\xc2\xbb\xb6'
                         b'\xbb\xbdWHITE*+WHITE+\xebWHITE>\xbb\xc0\xbb\xc2\xbb\xb6\xbb\xbdWHITE>'
                         b'\xbb\xc0\xbb\xc2\xbb\xb6\xbb\xbdABCDEF')

    def test_newlines(self):
        lines = "For(A,1,10", "Disp A", "End"
        self.assertEqual(TIProgram("\n".join(lines)), TIProgram("\r\n".join(lines)))

    def test_byte_literals(self):
        self.assertEqual(TIProgram.encode(r"\x26\uaa0AXYZ\0"), b'\x26\xaa\x0aXYZ\xbb\xd70')

        for leading_byte, prefix in TIToken.var_prefixes.items():
            self.assertEqual(TIProgram.encode(f"{prefix}0a"), bytes([leading_byte, 10]))

        with self.assertWarns(BytesWarning):
            self.assertEqual(TIProgram(r"List\x00").string(), "L₁")
            self.assertEqual(TIProgram(r"List\xff").string(), r"List\xff")
            self.assertEqual(TIProgram("String").string(), "String")
