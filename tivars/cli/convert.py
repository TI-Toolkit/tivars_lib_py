"""
Convert between file types
"""


import csv
import io
import json

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
        super().__init__(f"A {type(var).__name__} cannot be converted to {fmt}.")


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


def component_to_csv(var: TIComponent, **kwargs) -> bytes:
    """
    :return: A list of lists (CSV rows) representing ``var`` given some parameters, or errors
    """

    writer = csv.writer(outfile := io.StringIO(), delimiter=",")

    if isinstance(var, TIList):
        writer.writerow(var.list())

    elif isinstance(var, TIMatrix):
        writer.writerows(var.matrix())

    else:
        raise FormatError(var, "csv")

    outfile.seek(0)
    return outfile.read().encode()


def component_to_json(var: TIComponent, **kwargs) -> bytes:
    """
    :return: The JSON representation of ``var`` given some parameters, or errors
    """

    try:
        return json.dumps(var.json(**kwargs)).encode()

    except NotImplementedError:
        raise FormatError(var, "json")


def component_to_text(var: TIComponent, **kwargs) -> bytes:
    """
    :return: The text representation of ``var`` given some parameters, or errors
    """

    if var.__format__ == TIComponent.__format__:
        raise FormatError(var, "text")

    else:
        return var.string(**kwargs).encode()


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


def json_to_component(dct: dict, out_ext: str, **kwargs) -> TIComponent:
    """
    :return: The JSON ``dct`` converted to a `TIComponent` supporting file extension ``out_ext``
    """

    component = extension_to_type(out_ext)()
    component.load_dict(dct, **kwargs)
    return component


def text_to_component(text: str, out_ext: str, **kwargs) -> TIComponent:
    """
    :return: The text ``text`` converted to a `TIComponent` supporting file extension ``out_ext``
    """

    component = extension_to_type(out_ext)()
    component.load_string(text, **kwargs)
    return component
