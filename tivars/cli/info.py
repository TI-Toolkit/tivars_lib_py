import argparse
import re

from tivars.file import *
from tivars.flash import *
from tivars.models import *
from tivars.types import *
from tivars.var import *

from tivars.types.settings import SettingsEntry


def trim_list(lst: list, length: int, joiner: str = "\n") -> str:
    if len(lst) <= length:
        return joiner.join(lst)

    else:
        return joiner.join([*lst[:length], "..."])


def trim_string(string: str, length: int) -> str:
    if len(string) <= length:
        return string

    else:
        return string[:length] + "..."


def summarize_flash(flash: TIFlashFile) -> str:
    # Old f-string hacks
    joiner = "\n                   "
    regex = r"\[\w+\]"

    return "\n".join(f"""Header #{index + 1} Information
    Type           {type(header).__name__} (ID 0x{header.type_id})
    Name           {header.name}
    
    Revision No.   {header.revision}
    Revision Date  {header.date}
    
    Binary Format  0x{header.binary_flag:02x} ({'Intel' if header.binary_flag == 0x01 else 'binary'})
    Object Type    0x{header.object_type:02x}
    Device(s)      {', '.join(device.name for device, _ in header.devices)}
    
    Data           {trim_list([str(block) for block in header.data], 4, joiner) if header.binary_flag == 0x01
                    else trim_string(header.calc_data.hex(' ', -2), 50)}
    """ + (f"""
    License(s)     {', '.join(re.findall(regex, header.license))}
    """ if isinstance(header, TILicense) else "\n") for index, header in enumerate(flash.headers))


def summarize_var(var: TIVarFile) -> str:
    return summarize_header(var.header) + "\n" + summarize_entry(var.entries[0])


def summarize_header(header: TIHeader) -> str:
    return f"""Header Information
    Product ID  0x{header.product_id:02x}
    Model       {next((model for model in TIModel.MODELS if model.magic == header.magic and
                       model.product_id == header.product_id), 'unknown')} or newer
    Comment     {header.comment}
    """


def summarize_entry(entry: TIEntry) -> str:
    summary = f"""Entry Information
    Type           {type(entry).__name__} (ID 0x{entry.type_id:02x})
    Name           {entry.name}
    Version        0x{entry.version:02x}
    Archived?      {entry.archived}
    
    Data Length    {entry.calc_data_length}
    Compatibility  {entry.get_min_os().model} (OS {entry.get_min_os().version}) or newer
    Data           {trim_string(format(entry.calc_data, '2x'), 48)}
    """

    if isinstance(entry, TIMonoGDB):
        return summary + "\n" + summarize_gdb(entry)

    elif isinstance(entry, TIProgram):
        return summary + "\n" + summarize_program(entry)

    elif isinstance(entry, SettingsEntry):
        return summary + "\n" + summarize_settings(entry)

    else:
        try:
            return summary + f"    Value:      {trim_string(entry.string(), 48)}\n"

        except NotImplementedError:
            return summary + "\n"


def summarize_gdb(gdb: TIMonoGDB) -> str:
    def mode(flags, *options: str):
        return " | ".join(f"[{option}]" if getattr(type(flags), option) in flags else option for option in options)

    if isinstance(gdb, TIMonoSeqGDB):
        seq_modes = (f"{mode(gdb.extended_mode_flags, 'SEQ_n', 'SEQ_np1', 'SEQ_np2')}\n"
                     f"\n"
                     f"{mode(gdb.sequence_flags, 'Time', 'Web', 'uv', 'vw', 'uw')}")

    else:
        seq_modes = ""

    summary = f"""GDB Information
    Type             {gdb.mode}
    Has Color Data?  True
    
    Mode Settings    {mode(gdb.mode_flags, 'Sequential', 'Simul')}
                     {seq_modes}
                     {mode(gdb.mode_flags,'RectGC', 'PolarGC')}
                     {mode(gdb.mode_flags,'CoordOn', 'CoordOff')}
                     {mode(gdb.mode_flags, 'GridOff', 'GridDot', 'GridLine')}
                     GridColor: {gdb.grid_color.name}
                     Axes: {gdb.axes_color.name}
                     {mode(gdb.mode_flags, 'LabelOff', 'LabelOn')}
                     {mode(gdb.extended_mode_flags, 'ExprOn', 'ExprOff')}
                     BorderColor: {BorderColor(gdb.border_color)}

                     Detect Asymptotes: {'On' if GraphMode.DetectAsymptotesOn in gdb.color_mode_flags else 'Off'}
                       
    """ if isinstance(gdb, TIGDB) else f"""GDB Information
    Type             {gdb.mode}
    Has Color Data?  False

    Mode Settings    {mode(gdb.mode_flags, 'Connected', 'Dot')}
                     {mode(gdb.mode_flags, 'Sequential', 'Simul')}
                     {seq_modes}
                     {mode(gdb.mode_flags,'RectGC', 'PolarGC')}
                     {mode(gdb.mode_flags,'CoordOn', 'CoordOff')}           
                     {mode(gdb.mode_flags, 'GridOff', 'GridOn')}
                     {mode(gdb.mode_flags, 'AxesOn', 'AxesOff')}
                     {mode(gdb.mode_flags, 'LabelOff', 'LabelOn')}
                     {mode(gdb.extended_mode_flags, 'ExprOn', 'ExprOff')}

    """

    json = gdb.dict()
    summary += "\n    ".join(f"{var:9} {value}" for var, value in
                             (json["globalWindowSettings"] | json["specificData"]["settings"]).items())

    summary += "\n\n    "
    summary += "\n    ".join(f"{equation.json_name:9} {equation}" for equation in gdb.equations if equation.is_defined)

    return summary


def summarize_program(program: TIProgram) -> str:
    return f"""Program Information
    Length  {program.length}
    Lines   {len(program.lines())}
    
    Program {trim_string(format(program, 'a'), 48)}
    """


def summarize_settings(settings: SettingsEntry) -> str:
    return "Settings Information" + "\n    ".join(f"{var:9} {value}" for var, value in settings.dict().items())
