from tivars.bundle import *
from tivars.flash import *
from tivars.types import *
from tivars.models import *
from tivars.var import *


PACK_FORMATS = """
To make a TI-83 Premium CE bundle:
    b83, bundle (with --model in {TI_83PCE, TI_83PCEEP})
    
To make a TI-84 Plus CE bundle:
    b84, bundle (with --model in {TI_84PCE, TI_84PCET, TI_84PCEPY, TI_84PCETPE})
    
To make a group:
    8xg, group
    
To juxtapose entries in a single var file:
    juxt, var
    
To juxtapose flash headers in a single flash file:
    juxt, flash

"""


def pack_bundle(files: list[TIFile], *, name: str = None, model: TIModel = None) -> TIBundle:
    return TIBundle.bundle(files, name=name or "BUNDLE", model=model or TI_84PCE)


def pack_group(files: list[TIFile], *, name: str = None) -> TIGroup:
    entries = []
    for file in files:
        if not isinstance(file, TIVarFile):
            raise TypeError(f"File '{file.name}' cannot be put into a group.")

        entries.append(file.entries[0])

    return TIGroup.group(entries, name=name or "GROUP")

def pack_entries(files: list[TIFile], *, name: str = None) -> TIVarFile:
    var = TIVarFile(name=name or "UNNAMED")
    for file in files:
        if not isinstance(file, TIVarFile):
            raise TypeError(f"File '{file.name}' cannot be put into a var file.")

        var.add_entry(file.entries[0])

    return var


def pack_headers(files: list[TIFile], *, name: str = None) -> TIFlashFile:
    flash = TIFlashFile(name=name or "UNNAMED")
    for file in files:
        if not isinstance(file, TIFlashFile):
            raise TypeError(f"File '{file.name}' cannot be put into a flash file.")

        flash.add_header(file.headers[0])

    return flash
