import io

from tivars.file import *
from tivars.models import *
from tivars.tokenizer import *
from tivars.types import *


FORMATS = """
TIComplex         <-> text
TIEquation        <-> text
TIGDB             <-> json
TIImage           <-> png, jpeg, etc. (requires PIL)
TILicense         <-> text
TIList            <-> text
TIMatrix          <-> text
TIMonoPicture     <-> png, jpeg, etc. (requires PIL)
TIPicture         <-> png, jpeg, etc. (requires PIL)
TIProgram         <-> text
TIReal            <-> text
TIRecallWindow    <-> json
TIString          <-> text
TITableSettings   <-> json
TIWindowSettings  <-> json
"""


def get_type_from_extension(extension: str) -> type[TIEntry]:
    for var_type in TIEntry._type_ids.values():
        if var_type.extension == extension.replace("2", "x").replace("3", "x"):
            return var_type

    raise ValueError(f"could not identify extension '.{extension}'")


def image_to_image(in_file: bytes, in_format: str, out_format: str) -> bytes:
    try:
        from PIL import Image
        from tivars.PIL import TI8xiPlugin, TI8ciPlugin, TI8caPlugin

    except ImportError:
        raise ImportError("PIL is required to convert TI pictures/images to/from other formats")

    Image.open(in_file, "r", (in_format,)).save(out_file := io.BytesIO(), out_format)
    return out_file.read()


def entry_to_format(var: TIEntry, out_format: str, **kwargs):
    return getattr(var, out_format)(**kwargs)


def format_to_entry(data, in_format: str, var_type: type[TIEntry], **kwargs) -> TIEntry:
    entry = var_type()
    getattr(entry, f"load_{in_format}")(data, **kwargs)

    return entry


def repair(data: bytes) -> bytes:
    file = TIFile(data=data)

    if hasattr(file, "data"):
        file.data = file.data

    return file.bytes()
