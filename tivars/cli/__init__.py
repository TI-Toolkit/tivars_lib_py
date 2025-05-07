import argparse

from tivars.file import *
from .parser import *


def process(args: argparse.Namespace):
    print(args)


__all__ = ["parser", "process"]
