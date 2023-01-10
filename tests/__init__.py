import unittest


from tivars.models import *
from tivars.types import *


class TokenizationTests(unittest.TestCase):
    def test_load_from_file(self):
        test_program = TIProgram(model=TI_84p)

        test_program.open("tests/HELLO.8xp")
        with open("tests/HELLO.8xp", 'rb') as file:
            self.assertEqual(test_program.bytes(), file.read())
            file.seek(0)

            test_program.load(file)
            file.seek(0)
            self.assertEqual(test_program.bytes(), file.read())

    def test_load_from_string(self):
        test_program = TIProgram(name="HELLO", model=TI_84p)

        test_program.load_string(string := "Disp \"HELLO WORLD!\"")

        with open("tests/HELLO.8xp", 'rb') as file:
            self.assertEqual(test_program.bytes(), file.read())
            self.assertEqual(test_program.string(), string)

    def test_lots_of_chars(self):
        test_program = TIProgram(model=TI_84pce)

        with open("tests/CHARS2.8xp", 'rb') as file:
            test_program.load(file)
            file.seek(0)

            self.assertEqual(test_program.bytes(), file.read())

    def test_save_to_file(self):
        test_program = TIProgram(model=TI_84pce)

        test_program.open("tests/HELLO.8xp")
        test_program.save("tests/HELLO2.8xp")

        with open("tests/HELLO.8xp", 'rb') as orig:
            with open("tests/HELLO2.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())
