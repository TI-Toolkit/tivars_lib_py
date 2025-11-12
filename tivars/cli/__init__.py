import argparse
import os

from pathlib import Path
from warnings import catch_warnings, simplefilter

from .convert import *
from .pack import *
from .parser import *


def cli(args: argparse.Namespace = None):
    args = args or parser.parse_args()

    match args.subparser:
        case "convert":
            in_format = args.infile.split(".")[-1]
            out_format = args.format or (args.outfile or args.infile).split(".")[-1]

            match in_format := args.infile.split(".")[-1]:
                case "txt" | "md":
                    infile = Path(args.infile).read_text(encoding="utf8")

                    outfile = text_to_component(infile, out_format, lang=args.lang, model=args.model).bytes()

                case "json":
                    infile = json.load(file := open(args.infile))
                    file.close()

                    outfile = json_to_component(infile, out_format, lang=args.lang, model=args.model).bytes()

                case _:
                    try:
                        if in_format.startswith("8"):
                            infile = TIFile.open(args.infile)

                            if isinstance(infile, TIVarFile):
                                outfile = component_to_text(infile.entries[0]).encode()

                            elif isinstance(infile, TIFlashFile):
                                outfile = component_to_text(infile.headers[0]).encode()

                            else:
                                raise TypeError(f"Cannot convert file '{args.infile}.'")

                        else:
                            file = open(args.infile, "rb")
                            infile = file.read()
                            file.close()

                            outfile = image_to_image(infile, in_format, out_format)

                    except Exception:
                        raise ValueError(f"Unrecognized format '{out_format}'.")

            with open(args.outfile or f"UNNAMED.{out_format}", "rb+") as file:
                file.write(outfile)

        case "info":
            infile = TIFile.open(args.infile)

            with catch_warnings():
                if not args.warn:
                    simplefilter("ignore")

                if args.single:
                    if isinstance(infile, TIVarFile):
                        print(infile.entries[0].summary())
                        return

                    elif isinstance(infile, TIFlashFile):
                        print(infile.headers[0].summary())
                        return

                print(infile.summary())

        case "pack":
            files = [TIFile.open(file) for file in args.files]

            if not args.format:
                if not args.outfile:
                    raise ValueError("No pack format was specified.")

                out_format = args.outfile.split(".")[-1]

            else:
                out_format = args.format

            match out_format:
                case "b83":
                    outfile = pack_bundle(files, name=args.name, model=args.model or TI_83PCE)

                case "b84":
                    outfile = pack_bundle(files, name=args.name, model=args.model or TI_84PCE)

                case "bundle":
                    outfile = pack_bundle(files, name=args.name, model=args.model)

                case "8xg" | "group":
                    outfile = pack_group(files, name=args.name)

                case "juxt" | "var" | "flash":
                    if isinstance(files[0], TIVarFile) and out_format != "flash":
                        outfile = pack_entries(files, name=args.name)

                    elif isinstance(files[0], TIFlashFile) and out_format != "var":
                        outfile = pack_headers(files, name=args.name)

                    else:
                        raise TypeError(f"Cannot juxtapose passed files with format '{out_format}'.")

                case _:
                    raise ValueError(f"Unrecognized format '{out_format}'.")

            outfile.save(filename=args.outfile, model=args.model)

        case "unpack":
            infile = TIFile.open(args.infile)
            files = None

            if isinstance(infile, TIVarFile):
                # Group
                if len(infile.entries) == 1 and isinstance(entry := infile.entries[0], TIGroup):
                    files = entry.ungroup()

                # Juxtaposed files
                elif len(infile.entries) > 1:
                    files = infile.entries

            elif isinstance(infile, TIFlashFile):
                files = infile.headers

            elif isinstance(infile, TIBundle):
                files = infile.unbundle()


            if files is None:
                raise TypeError(f"File '{args.infile}' is not a container type.")

            if not files:
                print(f"Container '{args.infile}' is empty.")

            if args.outdir:
                os.makedirs(args.outdir, exist_ok=True)
                os.chdir(args.outdir)

            for file in files:
                file.save()

            print(f"Wrote {len(files)} file{'s' if len(files) > 1 else ''} to {os.getcwd()}.")


__all__ = ["parser", "cli"]
