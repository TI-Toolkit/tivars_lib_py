import io
import json

from tivars.file import *
from tivars.models import *
from tivars.types import *

from tivars.types.picture import PictureEntry


CONVERT_FORMATS = """
TIComplex         <-> json, txt
TIEquation        <-> json, txt
TIGDB             <-> json
TIGroup           <-> json
TIImage           <-> png, jpeg, etc. (requires PIL)
TILicense         <-> json, txt
TIList            <-> json, txt
TIMatrix          <-> json, txt
TIMonoPicture     <-> png, jpeg, etc. (requires PIL)
TIPicture         <-> png, jpeg, etc. (requires PIL)
TIProgram         <-> json, txt
TIReal            <-> json, txt
TIRecallWindow    <-> json
TIString          <-> json, txt
TITableSettings   <-> json
TIWindowSettings  <-> json
"""


def format_to_extension(fmt: str, *, model: TIModel) -> str:
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
    if subtype := TIComponent.get_type(extension=ext):
        return subtype

    raise TypeError(f"Extension '{ext}' does not correspond to a TI-(e)z80 type")


def component_to_json(var: TIComponent, **kwargs) -> str:
    try:
        return json.dumps(var.json(**kwargs))

    except NotImplementedError:
        raise TypeError(f"A {type(var).__name__} cannot be converted to json.")


def component_to_text(var: TIComponent, **kwargs) -> str:
    if var.__format__ == TIComponent.__format__:
        raise TypeError(f"A {type(var).__name__} cannot be converted to text.")

    else:
        return var.string(**kwargs)


def image_to_image(infile: bytes, out_ext: str) -> bytes:
    try:
        from PIL import Image
        from tivars.PIL import TI8xiPlugin, TI8ciPlugin, TI8caPlugin

    except ImportError:
        raise ImportError("PIL is required to convert TI-(e)z80 pictures/images to/from other formats")

    Image.open(infile, "r").save(outfile := io.BytesIO(), out_ext.upper())
    outfile.seek(0)
    return outfile.read()


def json_to_component(dct: dict, out_ext: str, **kwargs) -> TIComponent:
    component = extension_to_type(out_ext)()
    component.load_dict(dct, **kwargs)
    return component


def text_to_component(text: str, out_ext: str, **kwargs) -> TIComponent:
    component = extension_to_type(out_ext)()
    component.load_string(text, **kwargs)
    return component
