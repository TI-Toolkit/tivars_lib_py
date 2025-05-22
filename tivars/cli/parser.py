import argparse

from tivars.tokens.scripts.parse import MODEL_ORDER
from .convert import *

HELP_FORMATTER = lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=40, width=100)

parser = argparse.ArgumentParser(
    prog="tivars",
    description="CLI for viewing and converting TI-(e)z80 files",
    formatter_class=HELP_FORMATTER
)

MODEL_LIST = "\n".join("\t".join(f"{model:9}" for model in MODEL_ORDER if MODEL_ORDER[model] == order)
                       for order in {order: None for order in MODEL_ORDER.values() if 0 < order < 999999})

parser.add_argument("-m", "--models", action="version", version=MODEL_LIST,
                    help="show list of models and exit")
parser.add_argument("-v", "--version", action="version", version="tivars_lib_py 0.9.2",
                    help="show tivars_lib_py version and exit")

subparsers = parser.add_subparsers(title="modes", dest="subparser")

convert = subparsers.add_parser("convert",
                                description="Convert between file types",
                                help="Convert between file types",
                                formatter_class=HELP_FORMATTER)
convert.add_argument("infile",
                     help="input file")
convert.add_argument("-o", "--outfile", default=None,
                     help="output file (default: stdout)")
convert.add_argument("-f", "--format", default=None,
                     help="output format (default: format of <outfile>, or 'text')")
convert.add_argument("-l", "--lang", default="en",
                     help="output language code (default: 'en')")
convert.add_argument("-m", "--model", default=TI_84PCE,
                     help="output model target (default: 'TI-84+CE')")
convert.add_argument("--formats", action="version", version=FORMATS,
                     help="show list of supported formats and exit")

info = subparsers.add_parser("info",
                             description="Display information about a var file",
                             help="Display information about a var file",
                             formatter_class=HELP_FORMATTER)
info.add_argument("infile",
                  help="input file")
info.add_argument("-l", "--lang", default="en",
                  help="output language code (default: 'en')")
info.add_argument("-s", "--single", action="store_true",
                  help="only show the first entry/header in a file (default: false)")
info.add_argument("-w", "--warn", action="store_true",
                  help="whether to emit file warnings (default: false)")

pack = subparsers.add_parser("pack",
                             description="Pack files into a container type",
                             help="Pack files into a container type",
                             formatter_class=HELP_FORMATTER)
pack.add_argument("files", nargs="+",
                  help="files to pack; can be a directory or list of files")
pack.add_argument("-f", "--format", default=None,
                  help="pack format; can be a format type (e.g. 'bundle') or a file extension (e.g. 'b84')")
pack.add_argument("-m", "--model", default=TI_84PCE,
                  help="output model target (default: 'TI-84+CE')")
pack.add_argument("-n", "--name", default="UNNAMED",
                  help="output container name (default: <outfile>, or 'UNNAMED')")
pack.add_argument("-o", "--outfile", default=None,
                  help="output file (default: <name>.<format>)")

unpack = subparsers.add_parser("unpack",
                               description="Unpack files from a container type",
                               help="Unpack files from a container type",
                               formatter_class=HELP_FORMATTER)
unpack.add_argument("infile",
                    help="input file")
unpack.add_argument("-f", "--format", default=None,
                    help="pack format (default: inferred from <infile>)")
unpack.add_argument("-o", "--outdir", default=None,
                    help="output directory (will be created if nonexistent) (default: cwd)")

verify = subparsers.add_parser("verify",
                               description="Read a file and flag/repair improper data",
                               help="Read a file and flag/repair improper data",
                               formatter_class=HELP_FORMATTER)
verify.add_argument("infile",
                    help="input file")
verify.add_argument("-o", "--outfile", default=None,
                    help="output file if repairing (default: <infile>)")
verify.add_argument("-r", "--repair", action="store_true",
                    help="whether to repair <infile> if needed (default: false)")

__all__ = ["parser"]
