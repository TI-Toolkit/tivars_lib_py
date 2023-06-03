import io
import json

from typing import ByteString, Iterator
from warnings import warn

from tivars.models import *
from ..flags import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal
from .tokenized import TIEquation


class GraphMode(Flags):
    Dot = {0: 1}
    Connected = {0: 0}
    Simul = {1: 1}
    Sequential = {1: 0}
    GridOn = {2: 1, 7: 0}
    GridOff = {2: 0, 7: 0}
    GridLine = {2: 1, 7: 1}
    GridDot = {2: 1, 7: 0}
    PolarGC = {3: 1}
    RectGC = {3: 0}
    CoordOff = {4: 0}
    CoordOn = {4: 1}
    AxesOff = {5: 1}
    AxesOn = {5: 0}
    LabelOn = {6: 1}
    LabelOff = {6: 0}

    ExprOff = {0: 1}
    ExprOn = {0: 0}
    SEQ_n = {1: 0, 2: 0}
    SEQ_np1 = {1: 1, 2: 0}
    SEQ_np2 = {1: 0, 2: 1}

    DetectAsymptotesOn = {0: 1}
    DetectAsymptotesOff = {0: 0}


class SeqMode(Flags):
    Time = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    Web = {0: 1, 1: 0, 2: 0, 3: 0, 4: 0}
    VertWeb = {0: 0, 1: 1, 2: 0, 3: 0, 4: 0}
    uv = {0: 0, 1: 0, 2: 1, 3: 0, 4: 0}
    vw = {0: 0, 1: 0, 2: 0, 3: 1, 4: 0}
    uw = {0: 0, 1: 0, 2: 0, 3: 0, 4: 1}


class GraphStyle(Enum):
    SolidLine = b'\x00'
    ThickLine = b'\x01'
    ShadeAbove = b'\x02'
    ShadeBelow = b'\x03'
    Trace = b'\x04'
    Animate = b'\x05'
    DottedLine = b'\x06'

    _all = [SolidLine, ThickLine, ShadeAbove, ShadeBelow, Trace, Animate, DottedLine]
    STYLES = _all[:7]


class GraphColor(Enum):
    Mono = b'\x00'
    Blue = b'\x01'
    Red = b'\x02'
    Black = b'\x03'
    Magenta = b'\x04'
    Green = b'\x05'
    Orange = b'\x06'
    Brown = b'\x07'
    Navy = b'\x08'
    LtBlue = b'\x09'
    Yellow = b'\x0A'
    White = b'\x0B'
    LtGray = b'\x0C'
    MedGray = b'\x0D'
    Gray = b'\x0E'
    DarkGray = b'\x0F'

    _all = [Mono, Blue, Red, Black, Magenta, Green, Orange, Brown, Navy,
            LtBlue, Yellow, White, LtGray, MedGray, Gray, DarkGray]
    COLORS = _all[1:]


class GlobalStyle(Enum):
    Thick = b'\x00'
    DotThick = b'\x01'
    Thin = b'\x02'
    DotThin = b'\x03'

    _all = [Thick, Thin, DotThick, DotThin]
    STYLES = _all


class BorderColor(Enum):
    LtGray = b'\x01'
    Teal = b'\x02'
    LtBlue = b'\x03'
    White = b'\x04'

    _all = [LtGray, Teal, LtBlue, White]
    COLORS = _all


class EquationFlags(Flags):
    Selected = {5: 1}
    Deselected = {5: 0}
    UsedForGraph = {6: 1}
    UnusedForGraph = {6: 0}
    LinkTransferSet = {7: 1}
    LinkTransferClear = {7: 0}


class TIGraphedEquation(TIEquation):
    class Raw(TIEntry.Raw):
        __slots__ = "meta_length", "type_id", "name", "version", "archived", "flags", "style", "color", "data"

        def bytes(self) -> bytes:
            return self.meta_length + self.data_length + \
                self.type_id + self.name + self.version + self.archived + \
                self.data_length + self.flags + self.data

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.flags = EquationFlags()
        self.style = b'\x00'
        self.color = b'\x00'

    def __class_getitem__(cls, index: int):
        index -= 1

        class IndexedEquationConverter(Converter):
            _T = TIGraphedEquation

            @classmethod
            def get(cls, data: bytes, instance: 'TIMonoGDB') -> _T:
                return instance.equations[index]

            @classmethod
            def set(cls, value: _T, instance: 'TIMonoGDB') -> bytes:
                equations = list(instance.equations)
                equations[index] = value

                data = instance.raw.data[:instance.offset]
                for i in range(0, instance.num_equations, instance.num_equations // instance.num_styles):
                    data += equations[i].style

                data += b''.join(equation.raw.flags + equation.raw.data for equation in equations)

                if color := color_data(instance):
                    data += b'84C'
                    for i in range(0, instance.num_equations, instance.num_equations // instance.num_styles):
                        data += equations[i].color

                    data += color[-5:]

                return data

        return IndexedEquationConverter

    def __iter__(self) -> Iterator:
        return iter(self.dict().items())

    @Section(1, EquationFlags)
    def flags(self) -> EquationFlags:
        """
        The flags for the equation

        Whether the equation is selected, used for graphing, or is participating in a link transfer
        """

    @Section(1, GraphStyle)
    def style(self) -> bytes:
        """
        The style of the equation
        """

    @Section(1, GraphColor)
    def color(self) -> bytes:
        """
        The color of the equation
        """

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the tokens and their total size
        """

    @View(data, Integer)[0:2]
    def length(self) -> int:
        """
        The total size of the tokens
        """

    def load_data_section(self, data: io.BytesIO):
        self.raw.flags = data.read(1)
        data_length = int.from_bytes(length_bytes := data.read(2), 'little')
        self.raw.data = bytearray(length_bytes + data.read(data_length))

    @Loader[dict]
    def load_dict(self, dct: dict):
        self.style = getattr(GraphStyle, dct["style"])
        self.color = getattr(GraphColor, dct["color"])

        self.load_equation(TIEquation(dct["expr"]))

        flags = {"selected": False, "wasUsedForGraph": False, "linkTransfer": False} | dct["flags"]
        self.flags = EquationFlags()

        self.flags |= EquationFlags.Selected if flags["selected"] else EquationFlags.Deselected
        self.flags |= EquationFlags.UsedForGraph if flags["wasUsedForGraph"] else EquationFlags.UnusedForGraph
        self.flags |= EquationFlags.LinkTransferSet if flags["linkTransfer"] else EquationFlags.LinkTransferClear

    def dict(self) -> dict:
        dct = {"style": GraphStyle.get_name(self.style)}

        if self.color != GraphColor.Mono:
            dct["color"] = GraphColor.get_name(self.color)

        return dct | {
            "flags": {
                "selected": EquationFlags.Selected in self.flags,
                "wasUsedForGraph": EquationFlags.UsedForGraph in self.flags,
                "linkTransfer": EquationFlags.LinkTransferSet in self.flags
            },
            "expr": self.string()
        }

    @Loader[TIEquation]
    def load_equation(self, equation: TIEquation):
        self.raw.data = equation.data

    def equation(self) -> TIEquation:
        return TIEquation(self.bytes()[:-self.data_length - 1] + self.bytes()[-self.data_length:])

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None):
        equation = TIEquation()
        equation.load_string(string, model=model)
        self.load_equation(equation)


def color_data(gdb: 'TIMonoGDB') -> bytes:
    data = io.BytesIO(gdb.data[gdb.offset + gdb.num_styles:])
    for i in range(gdb.num_equations):
        TIGraphedEquation().load_data_section(data)

    return data.read()


class TIMonoGDB(TIEntry):
    extensions = {
        None: "8xd",
        TI_82: "82d",
        TI_83: "83d",
        TI_82A: "8xd",
        TI_82P: "8xd",
        TI_83P: "8xd",
        TI_84P: "8xd",
        TI_84T: "8xd",
        TI_84PCSE: "8xd",
        TI_84PCE: "8xd",
        TI_84PCEPY: "8xd",
        TI_83PCE: "8xd",
        TI_83PCEEP: "8xd",
        TI_82AEP: "8xd"
    }

    _type_id = b'\x08'
    mode_byte = 0x00

    min_data_length = 61

    num_equations = 0
    num_parameters = 0
    num_styles = 0

    equation_names = []

    def __iter__(self) -> Iterator:
        return iter(self.dict().items())

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[0:2]
    def length(self):
        """
        Two less than the length of the GDB
        """

    @View(data, Integer)[3:4]
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        One of 0x10, 0x20, 0x40, or 0x80
        """

    @View(data, GraphMode)[4:5]
    def mode_flags(self) -> GraphMode:
        """
        The flags for the mode settings

        Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
        """

    @View(data, GraphMode)[6:7]
    def extended_mode_flags(self) -> GraphMode:
        """
        The flags for the extended mode settings

        ExprOn/Off and sequence plot offsets for sequence mode
        """

    @View(data, TIReal)[7:16]
    def Xmin(self) -> TIReal:
        """
        Xmin: The leftmost graphscreen coordinate
        """

    @View(data, TIReal)[16:25]
    def Xmax(self) -> TIReal:
        """
        Xmax: The rightmost graphscreen coordinate
        """

    @View(data, TIReal)[25:34]
    def Xscl(self) -> TIReal:
        """
        Xscl: The separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[34:43]
    def Ymin(self) -> TIReal:
        """
        Ymin: The bottommost graphscreen coordinate
        """

    @View(data, TIReal)[43:52]
    def Ymax(self) -> TIReal:
        """
        Ymax: The topmost graphscreen coordinate
        """

    @View(data, TIReal)[52:61]
    def Yscl(self) -> TIReal:
        """
        Yscl: The separation between ticks on the vertical axis
        """

    @property
    def mode(self) -> str:
        """
        The mode for the GDB

        One of Function, Parametric, Polar, or Sequence
        """
        match self.mode_id:
            case TIMonoFuncGDB.mode_byte:
                return 'Function'
            case TIMonoParamGDB.mode_byte:
                return 'Parametric'
            case TIMonoPolarGDB.mode_byte:
                return 'Polar'
            case TIMonoSeqGDB.mode_byte:
                return 'Sequence'

            case _:
                warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                     BytesWarning)

    @property
    def offset(self) -> int:
        return TIMonoGDB.min_data_length + TIReal.data.width * self.num_parameters

    @property
    def equations(self) -> tuple[TIGraphedEquation, ...]:
        """
        The GDB's stored graph equations
        """

        data = io.BytesIO(self.data[self.offset:])
        equations = tuple(TIGraphedEquation(name=name) for name in self.equation_names)

        for i in range(self.num_styles):
            style = data.read(1)
            for j in range(r := self.num_equations // self.num_styles):
                equations[r * i + j].style = style

        for i in range(self.num_equations):
            equations[i].load_data_section(data)

        if rest := data.read():
            data = io.BytesIO(rest)
            data.seek(3, 1)

            for i in range(self.num_styles):
                color = data.read(1)
                for j in range(r := self.num_equations // self.num_styles):
                    equations[r * i + j].color = color

        return equations

    @Loader[dict]
    def load_dict(self, dct: dict):
        self.clear()
        self.raw.data[3] = {
            'Function': 0x10,
            'Parametric': 0x40,
            'Polar': 0x20,
            'Sequence': 0x80
        }.get(mode := dct.get("graphMode", "Function"), 0x00)

        for setting in dct.get("formatSettings", []):
            try:
                self.mode_flags |= getattr(GraphMode, setting)
            except AttributeError:
                warn(f"Unrecognized format setting ({setting}).",
                     UserWarning)

        ext_settings = dct.get("extSettings", {})
        if "showExpr" in ext_settings:
            self.extended_mode_flags |= GraphMode.ExprOn if ext_settings["showExpr"] else GraphMode.ExprOff

        if self.raw.data[3] != 0x80:
            if "seqMode" in ext_settings or "seqSettings" in dct:
                warn(f"Sequence settings have been provided, but this GDB is for {mode.lower()} graphs.",
                     UserWarning)

        for var, value in dct.get("globalWindowSettings", {}).items():
            if not hasattr(self, var):
                warn(f"Unrecognized window setting ({var}).",
                     UserWarning)
            else:
                setattr(self, var, TIReal(value))

        data = dct.get("specificData", {})
        for var, value in data.get("settings", {}).items():
            if not hasattr(self, var):
                warn(f"Unrecognized window setting ({var}).",
                     UserWarning)
            else:
                setattr(self, var, TIReal(value))

        for name, equation in data.get("equations", {}).items():
            if name in self.equation_names:
                plotted = TIGraphedEquation(name=name)
                plotted.load_dict(equation)
                setattr(self, name, plotted)

            else:
                warn(f"Unrecognized equation ({name}).",
                     UserWarning)

        if "global84CSettings" in dct:
            self.__class__ = TIGDB

        self.coerce()
        self._load_dict(dct)
        self.length = self.data_length - 2

    def _load_dict(self, dct: dict):
        pass

    def dict(self) -> dict:
        return {
            "graphMode": self.mode,
            "formatSettings": [
                "Dot" if GraphMode.Dot in self.mode_flags else "Connected",
                "Simul" if GraphMode.Simul in self.mode_flags else "Sequential",
                "GridOn" if GraphMode.GridOn in self.mode_flags else "GridOff",
                "PolarGC" if GraphMode.PolarGC in self.mode_flags else "RectGC",
                "CoordOff" if GraphMode.CoordOff in self.mode_flags else "CoordOn",
                "AxesOff" if GraphMode.AxesOff in self.mode_flags else "AxesOn",
                "LabelOn" if GraphMode.LabelOn in self.mode_flags else "LabelOff"
            ],
            "extSettings": {
                "showExpr": GraphMode.ExprOn in self.extended_mode_flags
            },
            "globalWindowSettings": {
                "Xmin": float(self.Xmin),
                "Xmax": float(self.Xmax),
                "Xscl": float(self.Xscl),
                "Ymin": float(self.Ymin),
                "Ymax": float(self.Ymax),
                "Yscl": float(self.Yscl)
            }
        }

    @Loader[str]
    def load_string(self, string: str):
        self.load_dict(json.loads(string))

    def string(self) -> str:
        return json.dumps(self.dict())

    def coerce(self):
        if color_data(self):
            self.__class__ = TIGDB
            self.set_length()
            self.coerce()
        else:
            match self.mode_id:
                case TIMonoFuncGDB.mode_byte:
                    self.__class__ = TIMonoFuncGDB
                case TIMonoParamGDB.mode_byte:
                    self.__class__ = TIMonoParamGDB
                case TIMonoPolarGDB.mode_byte:
                    self.__class__ = TIMonoPolarGDB
                case TIMonoSeqGDB.mode_byte:
                    self.__class__ = TIMonoSeqGDB

                case _:
                    warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                         BytesWarning)

            self.set_length()


class TIGDB(TIMonoGDB):
    min_data_length = 66

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.axes_color = GraphColor.Black
        self.grid_color = GraphColor.MedGray

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, GraphColor)[-5:-4]
    def grid_color(self) -> bytes:
        """
        The color of the grid
        """

    @View(data, GraphColor)[-4:-3]
    def axes_color(self) -> bytes:
        """
        The color of the axes
        """

    @View(data, GlobalStyle)[-3:-2]
    def global_style(self) -> bytes:
        """
        The line style for all plotted equations
        """

    @View(data, BorderColor)[-2:-1]
    def border_color(self) -> bytes:
        """
        The color of the graph border
        """

    @View(data, GraphMode)[-1:]
    def color_mode_flags(self) -> GraphMode:
        """
        The flags for extended color mode settings

        Only DetectAsymptotesOn/Off is stored here
        """

    def _load_dict(self, dct: dict):
        self.color_magic = "84C"

        if colors := dct.get("global84CSettings", {}).get("colors", {}):
            if "grid" in colors:
                self.grid_color = getattr(GraphColor, colors["grid"])

            if "axes" in colors:
                self.axes_color = getattr(GraphColor, colors["axes"])

            if "border" in colors:
                self.border_color = BorderColor.COLORS[colors["border"] - 1]

        if other := dct.get("global84CSettings", {}).get("other", {}):
            if "globalStyle" in other:
                self.global_style = getattr(GlobalStyle, other["globalStyle"])

            if "detectAsymptotes" in other:
                self.color_mode_flags |= \
                    GraphMode.DetectAsymptotesOn if other["detectAsymptotes"] else GraphMode.DetectAsymptotesOff

    def dict(self) -> dict:
        return {
            "global84CSettings": {
                "colors": {
                    "grid": GraphColor.get_name(self.grid_color),
                    "axes": GraphColor.get_name(self.axes_color),
                    "border": self.border_color[0]
                },
                "other": {
                    "globalStyle": GlobalStyle.get_name(self.global_style),
                    "detectAsymptotes": GraphMode.DetectAsymptotesOn in self.color_mode_flags
                }
            }
        }

    def coerce(self):
        match self.mode_id:
            case TIFuncGDB.mode_byte:
                self.__class__ = TIFuncGDB
            case TIParamGDB.mode_byte:
                self.__class__ = TIParamGDB
            case TIPolarGDB.mode_byte:
                self.__class__ = TIPolarGDB
            case TISeqGDB.mode_byte:
                self.__class__ = TISeqGDB

            case _:
                warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                     BytesWarning)

        self.set_length()


class TIMonoFuncGDB(TIMonoGDB):
    mode_byte = 0x10

    min_data_length = 110

    num_equations = 10
    num_parameters = 1
    num_styles = 10

    equation_names = ["Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "Y7", "Y8", "Y9", "Y0"]

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[3:4]
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        Always 0x10
        """

    @View(data, TIReal)[61:70]
    def Xres(self, value: TIReal) -> TIReal:
        """
        Xres: The pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer between 1 and 8, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIGraphedEquation[1])
    def Y1(self) -> TIGraphedEquation:
        """
        Y1: The 1st equation in function mode
        """

    @View(data, TIGraphedEquation[2])
    def Y2(self) -> TIGraphedEquation:
        """
        Y2: The 2nd equation in function mode
        """

    @View(data, TIGraphedEquation[3])
    def Y3(self) -> TIGraphedEquation:
        """
        Y3: The 3rd equation in function mode
        """

    @View(data, TIGraphedEquation[4])
    def Y4(self) -> TIGraphedEquation:
        """
        Y4: The 4th equation in function mode
        """

    @View(data, TIGraphedEquation[5])
    def Y5(self) -> TIGraphedEquation:
        """
        Y5: The 5th equation in function mode
        """

    @View(data, TIGraphedEquation[6])
    def Y6(self) -> TIGraphedEquation:
        """
        Y6: The 6th equation in function mode
        """

    @View(data, TIGraphedEquation[7])
    def Y7(self) -> TIGraphedEquation:
        """
        Y7: The 7th equation in function mode
        """

    @View(data, TIGraphedEquation[8])
    def Y8(self) -> TIGraphedEquation:
        """
        Y8: The 8th equation in function mode
        """

    @View(data, TIGraphedEquation[9])
    def Y9(self) -> TIGraphedEquation:
        """
        Y9: The 9th equation in function mode
        """

    @View(data, TIGraphedEquation[10])
    def Y0(self) -> TIGraphedEquation:
        """
        Y0: The 10th equation in function mode
        """

    @Loader[dict]
    def load_dict(self, dct: dict = None):
        if dct is None:
            with open("json/func.default.json") as file:
                dct = json.load(file)

        super().load_dict(dct)

    def dict(self) -> dict:
        return super().dict() | {
            "specificData": {
                "settings": {
                    "Xres": int(self.Xres)
                },
                "equations": {
                    equation.name: equation.dict() for equation in self.equations
                }
            }
        }


class TIFuncGDB(TIGDB, TIMonoFuncGDB):
    min_data_length = 128

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-18:-15]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    def mono(self) -> TIMonoFuncGDB:
        """
        Returns a copy of this GDB with all color data removed
        """

        return TIMonoFuncGDB(self.bytes()[:-18])

    def _load_dict(self, dct: dict):
        super(TIGDB, self)._load_dict(dct)
        super(TIFuncGDB, self)._load_dict(dct)

    def dict(self) -> dict:
        return super(TIGDB, self).dict() | super(TIFuncGDB, self).dict()


class TIMonoParamGDB(TIMonoGDB):
    mode_byte = 0x40

    min_data_length = 130

    num_equations = 12
    num_parameters = 3
    num_styles = 6

    equation_names = ["X1T", "Y1T", "X2T", "Y2T", "X3T", "Y3T", "X4T", "Y4T", "X5T", "Y5T", "X6T", "Y6T"]

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[3:4]
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        Always 0x40
        """

    @View(data, TIReal)[61:70]
    def Tmin(self) -> TIReal:
        """
        Tmin: The initial time
        """

    @View(data, TIReal)[70:79]
    def Tmax(self) -> TIReal:
        """
        Tmax: The final time
        """

    @View(data, TIReal)[79:88]
    def Tstep(self) -> TIReal:
        """
        Tstep: The time increment
        """

    @View(data, TIGraphedEquation[1])
    def X1T(self) -> TIGraphedEquation:
        """
        X1T: The 1st X-component in parametric mode
        """

    @View(data, TIGraphedEquation[2])
    def Y1T(self) -> TIGraphedEquation:
        """
        Y1T: The 1st Y-component in parametric mode
        """

    @View(data, TIGraphedEquation[3])
    def X2T(self) -> TIGraphedEquation:
        """
        X2T: The 2nd X-component in parametric mode
        """

    @View(data, TIGraphedEquation[4])
    def Y2T(self) -> TIGraphedEquation:
        """
        Y2T: The 2nd Y-component in parametric mode
        """

    @View(data, TIGraphedEquation[5])
    def X3T(self) -> TIGraphedEquation:
        """
        X3T: The 3rd X-component in parametric mode
        """

    @View(data, TIGraphedEquation[6])
    def Y3T(self) -> TIGraphedEquation:
        """
        Y3T: The 3rd Y-component in parametric mode
        """

    @View(data, TIGraphedEquation[7])
    def X4T(self) -> TIGraphedEquation:
        """
        X4T: The 4th X-component in parametric mode
        """

    @View(data, TIGraphedEquation[8])
    def Y4T(self) -> TIGraphedEquation:
        """
        Y4T: The 4th Y-component in parametric mode
        """

    @View(data, TIGraphedEquation[9])
    def X5T(self) -> TIGraphedEquation:
        """
        X5T: The 5th X-component in parametric mode
        """

    @View(data, TIGraphedEquation[10])
    def Y5T(self) -> TIGraphedEquation:
        """
        Y5T: The 5th Y-component in parametric mode
        """

    @View(data, TIGraphedEquation[11])
    def X6T(self) -> TIGraphedEquation:
        """
        X6T: The 6th X-component in parametric mode
        """

    @View(data, TIGraphedEquation[12])
    def Y6T(self) -> TIGraphedEquation:
        """
        Y6T: The 6th Y-component in parametric mode
        """

    @Loader[dict]
    def load_dict(self, dct: dict = None):
        if dct is None:
            with open("json/param.default.json") as file:
                dct = json.load(file)

        super().load_dict(dct)

    def _load_dict(self, dct: dict):
        for i in range(1, self.num_styles + 1):
            if (x_style := getattr(self, f"X{i}T").style) != (y_style := getattr(self, f"Y{i}T").style):
                warn(f"X and Y component styles do not agree (X{i}T: {x_style}, Y{i}T: {y_style}).",
                     UserWarning)

            if (x_color := getattr(self, f"X{i}T").color) != (y_color := getattr(self, f"Y{i}T").color):
                warn(f"X and Y component colors do not agree (X{i}T: {x_color}, Y{i}T: {y_color}).",
                     UserWarning)

    def dict(self) -> dict:
        return super().dict() | {
            "specificData": {
                "settings": {
                    "Tmin": float(self.Tmin),
                    "Tmax": float(self.Tmax),
                    "Tstep": float(self.Tstep),
                },
                "equations": {
                    equation.name: equation.dict() for equation in self.equations
                }
            }
        }


class TIParamGDB(TIGDB, TIMonoParamGDB):
    min_data_length = 144

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-14:-11]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    def mono(self) -> TIMonoParamGDB:
        """
        Returns a copy of this GDB with all color data removed
        """

        return TIMonoParamGDB(self.bytes()[:-14])

    def _load_dict(self, dct: dict):
        super(TIGDB, self)._load_dict(dct)
        super(TIParamGDB, self)._load_dict(dct)

    def dict(self) -> dict:
        return super(TIGDB, self).dict() | super(TIParamGDB, self).dict()


class TIMonoPolarGDB(TIMonoGDB):
    mode_byte = 0x20

    min_data_length = 112

    num_equations = 6
    num_parameters = 3
    num_styles = 6

    equation_names = ["r1", "r2", "r3", "r4", "r5", "r6"]

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[3:4]
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        Always 0x20
        """

    @View(data, TIReal)[61:70]
    def Thetamin(self) -> TIReal:
        """
        θmin: The initial angle
        """

    @View(data, TIReal)[70:79]
    def Thetamax(self) -> TIReal:
        """
        θmax: The final angle
        """

    @View(data, TIReal)[79:88]
    def Thetastep(self) -> TIReal:
        """
        θstep: The angle increment
        """

    @View(data, TIGraphedEquation[1])
    def r1(self) -> TIGraphedEquation:
        """
        r1: The 1st equation in polar mode
        """

    @View(data, TIGraphedEquation[2])
    def r2(self) -> TIGraphedEquation:
        """
        r1: The 2nd equation in polar mode
        """

    @View(data, TIGraphedEquation[3])
    def r3(self) -> TIGraphedEquation:
        """
        r3: The 3rd equation in polar mode
        """

    @View(data, TIGraphedEquation[4])
    def r4(self) -> TIGraphedEquation:
        """
        r4: The 4th equation in polar mode
        """

    @View(data, TIGraphedEquation[5])
    def r5(self) -> TIGraphedEquation:
        """
        r5: The 5th equation in polar mode
        """

    @View(data, TIGraphedEquation[6])
    def r6(self) -> TIGraphedEquation:
        """
        r6: The 6th equation in polar mode
        """

    @Loader[dict]
    def load_dict(self, dct: dict = None):
        if dct is None:
            with open("json/polar.default.json") as file:
                dct = json.load(file)

        super().load_dict(dct)

    def dict(self) -> dict:
        return super().dict() | {
            "specificData": {
                "settings": {
                    "Thetamin": float(self.Thetamin),
                    "Thetamax": float(self.Thetamax),
                    "Thetastep": float(self.Thetastep),
                },
                "equations": {
                    equation.name: equation.dict() for equation in self.equations
                }
            }
        }


class TIPolarGDB(TIGDB, TIMonoPolarGDB):
    min_data_length = 126

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-14:-11]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    def mono(self) -> TIMonoPolarGDB:
        """
        Returns a copy of this GDB with all color data removed
        """

        return TIMonoPolarGDB(self.bytes()[:-14])

    def _load_dict(self, dct: dict):
        super(TIGDB, self)._load_dict(dct)
        super(TIPolarGDB, self)._load_dict(dct)

    def dict(self) -> dict:
        return super(TIGDB, self).dict() | super(TIPolarGDB, self).dict()


class TIMonoSeqGDB(TIMonoGDB):
    mode_byte = 0x80

    min_data_length = 163

    num_equations = 3
    num_parameters = 10
    num_styles = 3

    equation_names = ["u", "v", "w"]

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[3:4]
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        Always 0x80
        """

    @View(data, GraphMode)[5:6]
    def sequence_flags(self) -> SeqMode:
        """
        The flags for the sequence mode settings
        """

    @View(data, TIReal)[61:70]
    def PlotStart(self, value) -> TIReal:
        """
        PlotStart: The initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[70:79]
    def nMax(self, value) -> TIReal:
        """
        nMax: The final value of n

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[79:88]
    def unMin(self) -> TIReal:
        """
        u(nMin): The initial value of u at nMin
        """

    @View(data, TIReal)[88:97]
    def vnMin(self) -> TIReal:
        """
        v(nMin): The initial value of v at nMin
        """

    @View(data, TIReal)[97:106]
    def nMin(self, value) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[106:115]
    def unMinp1(self) -> TIReal:
        """
        u(nMin + 1): The initial value of u at nMin + 1
        """

    @View(data, TIReal)[115:124]
    def vnMinp1(self) -> TIReal:
        """
        v(nMin + 1): The initial value of v at nMin + 1
        """

    @View(data, TIReal)[124:133]
    def wnMin(self) -> TIReal:
        """
        w(nMin): The initial value of w at nMin
        """

    @View(data, TIReal)[133:142]
    def PlotStep(self, value) -> TIReal:
        """
        PlotStep: The n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[142:151]
    def wnMinp1(self) -> TIReal:
        """
        w(nMin + 1): The initial value of w at nMin + 1
        """

    @View(data, TIGraphedEquation[1])
    def u(self) -> TIGraphedEquation:
        """
        u: The 1st equation in sequence mode
        """

    @View(data, TIGraphedEquation[2])
    def v(self) -> TIGraphedEquation:
        """
        v: The 2nd equation in sequence mode
        """

    @View(data, TIGraphedEquation[3])
    def w(self) -> TIGraphedEquation:
        """
        w: The 3rd equation in sequence mode
        """

    @Loader[dict]
    def load_dict(self, dct: dict = None):
        if dct is None:
            with open("json/seq.default.json") as file:
                dct = json.load(file)

        super().load_dict(dct)

    def _load_dict(self, dct: dict):
        ext_settings = dct.get("extSettings", {})
        if "seqMode" in ext_settings:
            match ext_settings["seqMode"]:
                case "SEQ(n)":
                    self.extended_mode_flags |= GraphMode.SEQ_n
                case "SEQ(n+1)":
                    self.extended_mode_flags |= GraphMode.SEQ_np1
                case "SEQ(n+2)":
                    self.extended_mode_flags |= GraphMode.SEQ_np2

        if "seqSettings" in dct:
            try:
                self.sequence_flags |= getattr(SeqMode, dct["seqMode"])
            except AttributeError:
                warn(f"Unrecognized sequence mode ({dct['seqMode']}).",
                     UserWarning)

    def dict(self) -> dict:
        dct = super().dict()

        match self.extended_mode_flags:
            case _SEQ_n if GraphMode.SEQ_n in self.extended_mode_flags:
                dct["extSettings"]["seqMode"] = "SEQ(n)"
            case _SEQ_np1 if GraphMode.SEQ_np1 in self.extended_mode_flags:
                dct["extSettings"]["seqMode"] = "SEQ(n+1)"
            case _SEQ_np2 if GraphMode.SEQ_np2 in self.extended_mode_flags:
                dct["extSettings"]["seqMode"] = "SEQ(n+2)"

        match self.sequence_flags:
            case _Time if SeqMode.Time in self.sequence_flags:
                dct["seqSettings"] = {"mode": "Time"}
            case _Web if SeqMode.Web in self.sequence_flags:
                dct["seqSettings"] = {"mode": "Web"}
            case _VertWeb if SeqMode.VertWeb in self.sequence_flags:
                dct["seqSettings"] = {"mode": "VertWeb"}
            case _uv if SeqMode.uv in self.sequence_flags:
                dct["seqSettings"] = {"mode": "uv"}
            case _vw if SeqMode.vw in self.sequence_flags:
                dct["seqSettings"] = {"mode": "vw"}
            case _uw if SeqMode.uw in self.sequence_flags:
                dct["seqSettings"] = {"mode": "uw"}

        return dct | {
            "specificData": {
                "settings": {
                    "nMin": int(self.nMin),
                    "nMax": int(self.nMax),
                    "PlotStart": int(self.PlotStart),
                    "PlotStep": int(self.PlotStep),
                    "unMin": float(self.unMin),
                    "unMinp1": float(self.unMinp1),
                    "vnMin": float(self.vnMinp1),
                    "vnMinp1": float(self.vnMinp1),
                    "wnMin": float(self.wnMin),
                    "wnMinp1": float(self.wnMinp1)
                },
                "equations": {
                    equation.name: equation.dict() for equation in self.equations
                }
            }
        }


class TISeqGDB(TIGDB, TIMonoSeqGDB):
    min_data_length = 174

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-11:-8]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    def mono(self) -> TIMonoSeqGDB:
        """
        Returns a copy of this GDB with all color data removed
        """

        return TIMonoSeqGDB(self.bytes()[:-11])

    def _load_dict(self, dct: dict):
        super(TIGDB, self)._load_dict(dct)
        super(TISeqGDB, self)._load_dict(dct)

    def dict(self) -> dict:
        return super(TIGDB, self).dict() | super(TISeqGDB, self).dict()


__all__ = ["TIMonoGDB", "TIMonoFuncGDB", "TIMonoParamGDB", "TIMonoPolarGDB", "TIMonoSeqGDB",
           "TIGDB", "TIFuncGDB", "TIParamGDB", "TIPolarGDB", "TISeqGDB",
           "TIGraphedEquation", "GraphMode", "GraphStyle", "GraphColor", "GlobalStyle"]
