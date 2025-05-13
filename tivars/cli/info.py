from tivars.file import *
from tivars.models import *
from tivars.types import *
from tivars.var import *

from tivars.types.settings import SettingsEntry


def trim(string: str, length: int):
    if len(string) <= length:
        return string

    else:
        return string[:length] + "..."


def dump(file: TIFile):
    pass


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
    Data           {trim(format(entry, "2x"), 49)}
    """

    if isinstance(entry, TIMonoGDB):
        return summary + "\n" + summarize_gdb(entry)

    elif isinstance(entry, TIProgram):
        return summary + "\n" + summarize_program(entry)

    elif isinstance(entry, SettingsEntry):
        return summary + "\n" + summarize_settings(entry)

    else:
        try:
            return summary + f"    Value:      {trim(entry.string(), 48)}\n"

        except NotImplementedError:
            return summary + "\n"


def summarize_gdb(gdb: TIMonoGDB) -> str:
    def mode(flags, *options: str):
        return " | ".join(f"[{option}]" if getattr(type(flags), option) in flags else option for option in options)

    if isinstance(gdb, TIMonoSeqGDB):
        seq_modes = (f"{mode(gdb.extended_mode_flags, "SEQ_n", "SEQ_np1", "SEQ_np2")}\n"
                     f"\n"
                     f"{mode(gdb.sequence_flags, "Time", "Web", "uv", "vw", "uw")}")

    else:
        seq_modes = ""

    summary = f"""GDB Information
    Type             {gdb.mode}
    Has Color Data?  True
    
    Mode Settings    {mode(gdb.mode_flags, "Sequential", "Simul")}
                     {seq_modes}
                     {mode(gdb.mode_flags,"RectGC", "PolarGC")}
                     {mode(gdb.mode_flags,"CoordOn", "CoordOff")}
                     {mode(gdb.mode_flags, "GridOff", "GridDot", "GridLine")}
                     GridColor: {gdb.grid_color.name}
                     Axes: {gdb.axes_color.name}
                     {mode(gdb.mode_flags, "LabelOff", "LabelOn")}
                     {mode(gdb.extended_mode_flags, "ExprOn", "ExprOff")}
                     BorderColor: {BorderColor.get_name(gdb.border_color)}

                     Detect Asymptotes: {'On' if GraphMode.DetectAsymptotesOn in gdb.color_mode_flags else 'Off'}
                       
    """ if isinstance(gdb, TIGDB) else f"""GDB Information
    Type             {gdb.mode}
    Has Color Data?  False

    Mode Settings    {mode(gdb.mode_flags, "Connected", "Dot")}
                     {mode(gdb.mode_flags, "Sequential", "Simul")}
                     {seq_modes}
                     {mode(gdb.mode_flags,"RectGC", "PolarGC")}
                     {mode(gdb.mode_flags,"CoordOn", "CoordOff")}           
                     {mode(gdb.mode_flags, "GridOff", "GridOn")}
                     {mode(gdb.mode_flags, "AxesOn", "AxesOff")}
                     {mode(gdb.mode_flags, "LabelOff", "LabelOn")}
                     {mode(gdb.extended_mode_flags, "ExprOn", "ExprOff")}

    """

    json = gdb.dict()
    summary += "\n    ".join(f"{var:9} {value}" for var, value in
                             (json["globalWindowSettings"] | json["specificData"]["settings"]).items())

    summary += "\n\n    "
    summary += "\n    ".join(f"{equation.json_name:9} {equation}" for equation in gdb.equations if equation.is_defined)

    return summary


def summarize_program(program: TIProgram) -> str:
    return f"""Program Information
    Length {program.length}
    Lines  {len(program.lines())}
    
    """


def summarize_settings(settings: SettingsEntry) -> str:
    return "Settings Information" + "\n    ".join(f"{var:9} {value}" for var, value in settings.dict().items())
