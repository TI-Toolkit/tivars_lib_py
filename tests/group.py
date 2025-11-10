import unittest

from tivars.types import *


class GroupTests(unittest.TestCase):
    def test_group(self):
        test_group = TIGroup()

        with open("tests/data/var/Group.8xg", 'rb') as file:
            test_group.load_from_file(file)
            file.seek(0)

            self.assertEqual(test_group.bytes(), file.read()[55:-2])

        ungrouped = test_group.ungroup()

        self.assertEqual(ungrouped[0], TIEquation("10sin(theta", name="r1"))
        self.assertEqual(type(ungrouped[1]), TIWindowSettings)

        self.assertEqual(TIGroup.group(ungrouped).ungroup(), ungrouped)
        self.assertEqual(TIGroup(ungrouped).ungroup(), ungrouped)
