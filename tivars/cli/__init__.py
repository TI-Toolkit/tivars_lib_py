import contextlib
import glob
import os

from pathlib import Path
from warnings import catch_warnings, simplefilter

from .convert import *
from .pack import *
from .parser import *


def cli(*args, **kwargs):
    if args or kwargs:
        args = [*args, *[f"--{key}={value}" for key, value in kwargs.items()]]

    else:
        args = None

    args = parser.parse_args(args)
    if hasattr(args, "model") and isinstance(args.model, str):
        args.model = TIModel.from_name(args.model)

    match args.subparser:
        case "convert":
            in_ext = Path(args.infile).suffix.removeprefix(".")
            out_ext = format_to_extension(args.format or Path(args.outfile or args.infile).suffix.removeprefix("."), model=args.model)
            name = args.name

            if in_ext == out_ext:
                print("Successfully did nothing.")
                return

            try:
                match in_ext:
                    case "txt" | "md":
                        text = Path(args.infile).read_text(encoding="utf8")

                        text_to_component(text, out_ext, lang=args.lang, model=args.model).save(args.name, model=args.model)

                    case "json":
                        with open(args.infile) as file:
                            dct = json.load(file)

                        json_to_component(dct, out_ext, lang=args.lang, model=args.model).save(args.name, model=args.model)

                    case _:
                        try:
                            outfile = image_to_image(args.infile, out_ext)

                        except Exception as e:
                            infile = extension_to_type(in_ext).open(args.infile)
                            name = infile.name

                            match out_ext:
                                case "txt":
                                    outfile = component_to_text(infile, lang=args.lang, model=args.model).encode()

                                case "json":
                                    outfile = json.dumps(component_to_json(infile, lang=args.lang, model=args.model))

                                case _:
                                    raise TypeError(f"Format '{in_ext}' not recognized.")

                        filename = (name or Path(args.infile).stem) + "." + out_ext
                        with open(args.outfile or filename, "wb+") as file:
                            file.write(outfile)

            except Exception as e:
                raise ValueError(f"Cannot convert file '{args.infile}' to format '{out_ext}'.") from None

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
            if len(args.files) == 1 and os.path.isdir(args.files[0]):
                args.files = glob.glob(f"{args.files[0]}/*")

            files = [TIFile.open(file) for file in args.files if os.path.isfile(file)]
            if not files:
                raise ValueError("No files were passed")

            if not args.format:
                if not args.outfile:
                    raise ValueError("No pack format was specified.")

                out_ext = args.outfile.split(".")[-1]

            else:
                out_ext = args.format

            match out_ext:
                case "b83":
                    outfile = pack_bundle(files, name=args.name, model=args.model or TI_83PCE)

                case "b84":
                    outfile = pack_bundle(files, name=args.name, model=args.model or TI_84PCE)

                case "bundle":
                    outfile = pack_bundle(files, name=args.name, model=args.model)

                case "8xg" | "group":
                    outfile = pack_group(files, name=args.name)

                case "juxt" | "var" | "flash":
                    if isinstance(files[0], TIVarFile) and out_ext != "flash":
                        outfile = pack_entries(files, name=args.name)

                    elif isinstance(files[0], TIFlashFile) and out_ext != "var":
                        outfile = pack_headers(files, name=args.name)

                    else:
                        raise TypeError(f"Cannot juxtapose passed files with format '{out_ext}'.")

                case _:
                    raise ValueError(f"Unrecognized format '{out_ext}'.")

            outfile.save(filename=args.outfile, model=args.model)
            print(f"Packed {len(files)} file{'s' if len(files) > 1 else ''}.")

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

            os.makedirs(args.outdir, exist_ok=True)
            with contextlib.chdir(args.outdir):
                for file in files:
                    file.save()

                print(f"Wrote {len(files)} file{'s' if len(files) > 1 else ''} to {os.getcwd()}.")


__all__ = ["parser", "cli"]
