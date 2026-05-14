"""
Convert between file types
"""


import csv
import io
import json
import string

from tivars.file import *
from tivars.models import *
from tivars.types import *


CONVERT_FORMATS = """
TIComplex         <-> json, txt
TIEquation        <-> json, txt
TIGDB             <-> json
TIGroup           <-> json
TIImage           <-> png, jpeg, etc. (requires PIL)
TILicense         <-> json, txt
TIList            <-> csv, json, txt
TIMatrix          <-> csv, json, txt
TIMonoPicture     <-> png, jpeg, etc. (requires PIL)
TIPicture         <-> png, jpeg, etc. (requires PIL)
TIProgram         <-> json, txt
TIReal            <-> json, txt
TIRecallWindow    <-> json
TIString          <-> json, txt
TITableSettings   <-> json
TIWindowSettings  <-> json
"""


class FormatError(TypeError):
    def __init__(self, var: TIComponent, fmt: str):
        super().__init__(f"A {type(var).__name__} cannot be converted to/from {fmt}.")


def format_to_extension(fmt: str, *, model: TIModel) -> str:
    """
    :return: The file extension for ``fmt`` corresponding to ``model``
    """

    subclasses = TIEntry.__subclasses__()
    while subclasses:
        subclass = subclasses.pop(0)
        if subclass.__name__.upper().removeprefix("TI") == fmt.upper().removeprefix("TI"):
            return subclass.get_extension(model)

        subclasses.extend(subclass.__subclasses__())

    match fmt.removeprefix("."):
        case "txt" | "text" | "md":
            return "txt"

        case ext:
            return ext


def extension_to_type(ext: str) -> type[TIComponent]:
    """
    :return: The `TIComponent` subtype having extension ``ext``
    """

    if subtype := TIComponent.get_type(extension=ext):
        return subtype

    raise TypeError(f"Extension '{ext}' does not correspond to a TI-(e)z80 type")


def component_to_csv(component: TIComponent, **kwargs) -> bytes:
    """
    :return: A list of lists (CSV rows) representing ``component`` given some parameters, or errors
    """

    writer = csv.writer(outfile := io.StringIO(), delimiter=",")

    if isinstance(component, TIList):
        writer.writerow(component.list())

    elif isinstance(component, TIMatrix):
        writer.writerows(component.matrix())

    else:
        raise FormatError(component, "csv")

    outfile.seek(0)
    return outfile.read().encode()


def component_to_json(component: TIComponent, **kwargs) -> bytes:
    """
    :return: The JSON representation of ``component`` given some parameters, or errors
    """

    try:
        return json.dumps(component.json(**kwargs)).encode()

    except NotImplementedError:
        raise FormatError(component, "json")


def component_to_text(component: TIComponent, **kwargs) -> bytes:
    """
    :return: The text representation of ``component`` given some parameters, or errors
    """

    if component.__format__ == TIComponent.__format__:
        raise FormatError(component, "text")

    else:
        return component.string(**kwargs).encode()


def image_to_image(infile: bytes, out_ext: str) -> bytes:
    """
    :return: The bytes of ``infile`` in ``out_ext`` format, or errors
    """

    try:
        from PIL import Image
        from tivars.PIL import TI8xiPlugin, TI8ciPlugin, TI8caPlugin

    except ImportError:
        raise ImportError("PIL is required to convert TI-(e)z80 pictures/images to/from other formats")

    Image.open(infile, "r").save(outfile := io.BytesIO(), out_ext.upper())
    outfile.seek(0)
    return outfile.read()


def csv_to_component(contents: str, out_ext: str, args):
    """
    :return: The csv ``rows`` converted to a `TIComponent` (or perhaps several) supporting file extension ``out_ext``
    """

    reader = iter(csv.reader(lines := contents.splitlines()))
    if csv.Sniffer().has_header(contents) and len(lines) > 1:
        names = next(reader)

    elif len(lines[0]) <= 6:
        names = ["L1", "L2", "L3", "L4", "L5", "L6"]

    else:
        names = list(string.ascii_uppercase)

    component_type = extension_to_type(out_ext)
    if issubclass(component_type, TIList):
        if len(lines) == 1:
            names = [args.name]
            lists = [next(reader)]

        else:
            lists = zip(*reader)

        for name, lst in zip(names, lists):
            component = component_type(name=name)
            component.load_list(lst)
            component.save(args.outfile, model=args.model)

    elif issubclass(component_type, TIMatrix):
        component = component_type(name=args.name)
        component.load_matrix(list(reader))
        component.save(args.outfile, model=args.model)

    else:
        raise FormatError(component_type(), "csv")


def json_to_component(dct: dict, out_ext: str, args):
    """
    :return: The JSON ``dct`` converted to a `TIComponent` supporting file extension ``out_ext``
    """

    component = extension_to_type(out_ext)(name=args.name)
    component.load_dict(dct, lang=args.lang, model=args.model)
    component.save(args.outfile, model=args.model)


def text_to_component(text: str, out_ext: str, args):
    """
    :return: The text ``text`` converted to a `TIComponent` supporting file extension ``out_ext``
    """

    component = extension_to_type(out_ext)(name=args.name)
    component.load_string(text, lang=args.lang, model=args.model)
    component.save(args.outfile, model=args.model)
