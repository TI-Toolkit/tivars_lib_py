import argparse

from tivars.file import *
from .parser import *


def cli(args: argparse.Namespace = None):
    args = args or parser.parse_args()
    print(args)


__all__ = ["parser", "cli"]
