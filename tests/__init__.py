import unittest


from tivars.models import *
from tivars.vars.types import *


class TokenizationTests(unittest.TestCase):
    def test_load_from_file(self):
        test_program = TIProgram("HELLO", TI_84pce)

        with open("tests/HELLO.8xp", 'rb') as file:
            test_program.load(file)
            file.seek(0)

            self.assertEqual(test_program.dump(), file.read())

    def test_load_from_string(self):
        test_program = TIProgram("HELLO", TI_84pce)

        test_program.loads(string := "Disp \"HELLO WORLD!\"")

        with open("tests/HELLO.8xp", 'rb') as file:
            self.assertEqual(test_program.dump(), file.read())
            self.assertEqual(test_program.dumps(), string)

    def test_lots_of_chars(self):
        test_program = TIProgram("CHARS2", TI_84pce)

        with open("tests/CHARS2.8xp", 'rb') as file:
            test_program.load(file)
            file.seek(0)

            self.assertEqual(test_program.dump(), file.read())

    def test_save_to_file(self):
        test_program = TIProgram("HELLO", TI_84pce)

        with open("tests/HELLO.8xp", 'rb') as file:
            test_program.load(file)

        test_program.save("tests/HELLO2.8xp")

        with open("tests/HELLO.8xp", 'rb') as orig:
            with open("tests/HELLO2.8xp", 'rb') as new:
                self.assertEqual(new.read(), orig.read())
