import argparse

from warnings import catch_warnings, simplefilter

from tivars.file import *
from .parser import *


def cli(args: argparse.Namespace = None):
    args = args or parser.parse_args()

    match args.subparser:
        case "info":
            with catch_warnings():
                if not args.warn:
                    simplefilter("ignore")

                print(TIFile.open(args.infile).summary())


__all__ = ["parser", "cli"]
