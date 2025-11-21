import io
import json

from tivars.file import *
from tivars.models import *
from tivars.tokenizer import *
from tivars.types import *


CONVERT_FORMATS = """
TIComplex         <-> txt
TIEquation        <-> txt
TIGDB             <-> json
TIImage           <-> png, jpeg, etc. (requires PIL)
TILicense         <-> txt
TIList            <-> txt
TIMatrix          <-> txt
TIMonoPicture     <-> png, jpeg, etc. (requires PIL)
TIPicture         <-> png, jpeg, etc. (requires PIL)
TIProgram         <-> txt
TIReal            <-> txt
TIRecallWindow    <-> json
TIString          <-> txt
TITableSettings   <-> json
TIWindowSettings  <-> json
"""


def get_format(fmt: str) -> type[TIComponent] | str:
    if fmt in ("txt", "text", "md"):
        return "txt"

    elif fmt == "json":
        return "json"

    elif fmt.startswith("8"):
        if fmt.endswith("u"):
            return TILicense

        return TIEntry.get_type(extension=fmt)

    else:
        subclasses = TIComponent.__subclasses__()
        while subclasses:
            subclass = subclasses.pop(0)
            if subclass.__name__.upper().removeprefix("TI") == fmt.upper().removeprefix("TI"):
                return subclass

            subclasses.extend(subclass.__subclasses__())

        return fmt


def component_to_json(var: TIComponent, **kwargs) -> str:
    if isinstance(var, (TIGDB, TIRecallWindow, TITableSettings, TIWindowSettings)):
        return json.dumps(var.json(**kwargs))

    else:
        raise TypeError(f"A {type(var).__name__} cannot be converted to json.")


def component_to_text(var: TIComponent, **kwargs) -> str:
    try:
        return component_to_json(var)

    except TypeError:
        if isinstance(var, (TIImage, TIMonoPicture, TIPicture)):
            raise TypeError(f"A {type(var).__name__} cannot be converted to text.")

        else:
            return var.string(**kwargs)


def image_to_image(infile: bytes, out_format: str) -> bytes:
    try:
        from PIL import Image
        from tivars.PIL import TI8xiPlugin, TI8ciPlugin, TI8caPlugin

    except ImportError:
        raise ImportError("PIL is required to convert TI pictures/images to/from other formats")

    Image.open(infile, "r").save(outfile := io.BytesIO(), out_format.upper())
    outfile.seek(0)
    return outfile.read()


def json_to_component(dct: dict, out_format: type[TIComponent], **kwargs) -> TIComponent:
    component = out_format()
    component.load_dict(dct, **kwargs)
    return component


def text_to_component(text: str, out_format: type[TIComponent], **kwargs) -> TIComponent:
    component = out_format()
    component.load_string(text, **kwargs)
    return component
