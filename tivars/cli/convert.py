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


def component_to_json(var: TIComponent) -> str:
    if isinstance(var, (TIGDB, TIRecallWindow, TITableSettings, TIWindowSettings)):
        return json.dumps(var.json())

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


def image_to_image(infile: bytes, in_format: str, out_format: str) -> bytes:
    try:
        from PIL import Image
        from tivars.PIL import TI8xiPlugin, TI8ciPlugin, TI8caPlugin

    except ImportError:
        raise ImportError("PIL is required to convert TI pictures/images to/from other formats")

    Image.open(infile, "r", (in_format,)).save(out_file := io.BytesIO(), out_format)
    return out_file.read()


def json_to_component(text: str, out_format: type[TIComponent], **kwargs) -> TIComponent:
    try:
        component = out_format()
        component.load_dict(json.loads(text), **kwargs)
        return component

    except NotImplementedError:
        raise TypeError(f"A {out_format.__name__} cannot be loaded from json.")


def text_to_component(text: str, out_format: type[TIComponent], **kwargs) -> TIComponent:
    try:
        component = out_format()
        component.load_string(text, **kwargs)
        return component

    except NotImplementedError:
        raise TypeError(f"A {out_format.__name__} cannot be loaded from text.")
