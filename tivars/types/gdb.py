import io
import json

from typing import ByteString
from warnings import warn

from tivars.models import *
from ..flags import *
from ..data import *
from ..var import TIEntry, TIEntryRaw
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

    Thin = b'\x00'
    Thick = b'\x01'
    DotThick = b'\x06'
    DotThin = b'\x07'

    _all = [SolidLine, ThickLine, ShadeBelow, ShadeBelow, Trace, Animate, DottedLine, Thin, Thick, DotThick, DotThin]
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


class TIGraphedEquationRaw(TIEntryRaw):
    __slots__ = "meta_length", "_data_length", "type_id", "name", "version", "archived", "_data_length", \
                "flags", "__style", "__color", "data"


class TIGraphedEquation(TIEquation):
    _raw_class = TIGraphedEquationRaw

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: ByteString = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.flags = EquationFlags()
        self.style = b'\x00'
        self.color = b'\x00'

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
        data_length = int.from_bytes(data.read(2), 'little')
        self.raw.data = int.to_bytes(data_length, 2, 'little') + data.read(data_length)

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
        return {"style": GraphStyle.get_name(self.style),
                "color": GraphColor.get_name(self.color),
                "expr": self.string(),
                "flags": {"selected": EquationFlags.Selected in self.flags,
                          "wasUsedForGraph": EquationFlags.UsedForGraph in self.flags,
                          "linkTransfer": EquationFlags.LinkTransferSet in self.flags}
                }

    def load_equation(self, equation: TIEquation):
        self.raw.data = equation.data

    def equation(self) -> TIEquation:
        return TIEquation(self.bytes()[:-self.data_length - 1] + self.bytes()[-self.data_length:])

    def load_string(self, string: str, *, model: TIModel = None):
        equation = TIEquation()
        equation.load_string(string, model=model)
        self.load_equation(equation)


def color_data(gdb: 'TIMonoGDB') -> bytes:
    data = io.BytesIO(gdb.data[gdb.offset + gdb.num_styles:])
    for i in range(gdb.num_equations):
        TIGraphedEquation().load_data_section(data)

    return data.read()


def IndexedEquation(index: int):
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

            data = b''
            for i in range(instance.num_styles):
                data += equations[i].style
                i += instance.num_equations // instance.num_styles

            data += b''.join(equation.raw.flags + equation.raw.data for equation in equations)

            if color_data(instance):
                for i in range(instance.num_styles):
                    data += equations[i].color
                    i += instance.num_equations // instance.num_styles

            return instance.raw.data[:instance.offset] + data

    return IndexedEquationConverter


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

    num_equations = 0
    num_parameters = 0
    num_styles = 0

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

    @property
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        One of 0x10, 0x20, 0x40, or 0x80
        """
        return self.data[3]

    @property
    def mode(self) -> str:
        """
        The mode for the GDB

        One of Function, Parametric, Polar, or Sequence
        """
        match self.mode_id:
            case 0x10: return 'Function'
            case 0x40: return 'Parametric'
            case 0x20: return 'Polar'
            case 0x80: return 'Sequence'

            case _: warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                         BytesWarning)

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
        Xmin: the smallest or leftmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[16:25]
    def Xmax(self) -> TIReal:
        """
        Xmax: the largest or rightmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[25:34]
    def Xscl(self) -> TIReal:
        """
        Xscl: the separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[34:43]
    def Ymin(self) -> TIReal:
        """
        Ymin: the smallest or bottommost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[43:52]
    def Ymax(self) -> TIReal:
        """
        Ymax: the largest or topmost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[52:61]
    def Yscl(self) -> TIReal:
        """
        Yscl: the separation between ticks on the vertical axis
        """

    @property
    def offset(self) -> int:
        return 61 + TIReal.data.width * self.num_parameters

    @property
    def equations(self) -> tuple[TIGraphedEquation, ...]:
        """
        The GDB's stored graph equations
        """

        data = io.BytesIO(self.data[self.offset:])
        equations = tuple(TIGraphedEquation() for _ in range(self.num_equations))

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

    def load_dict(self, dct: dict):
        self.raw.data = bytearray(61)
        self.raw.data[3] = {'Function': 0x10,
                            'Parametric': 0x40,
                            'Polar': 0x20,
                            'Sequence': 0x80}.get(dct.get("graphMode", "Function"), 0x00)

        for setting in dct.get("formatSettings", []):
            self.mode_flags |= getattr(GraphMode, setting)

        ext_settings = dct.get("extSettings", {})
        if "showExpr" in ext_settings:
            self.extended_mode_flags |= GraphMode.ExprOn if ext_settings["showExpr"] else GraphMode.ExprOff

        match ext_settings.get("seqMode", ""):
            case "SEQ(n)": self.extended_mode_flags |= GraphMode.SEQ_n
            case "SEQ(n+1)": self.extended_mode_flags |= GraphMode.SEQ_np1
            case "SEQ(n+2)": self.extended_mode_flags |= GraphMode.SEQ_np2

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
            if hasattr(self, name):
                plotted = TIGraphedEquation(name=name)
                plotted.load_dict(equation)
                setattr(self, name, plotted)

            else:
                warn(f"Unrecognized equation ({name}).",
                     UserWarning)

        if "global84CSettings" in dct or "colors" in data:
            self.__class__ = TIGDB

        self.coerce()
        self._load_dict(dct)

    def _load_dict(self, dct: dict):
        pass

    def dict(self) -> dict:
        raise NotImplementedError

    def load_string(self, string: str):
        self.load_dict(json.loads(string))

    def string(self) -> str:
        return json.dumps(self.dict())

    def coerce(self):
        if color_data(self):
            self.__class__ = TIGDB
            self.coerce()
        else:
            match self.mode_id:
                case 0x10: self.__class__ = TIMonoFuncGDB
                case 0x40: self.__class__ = TIMonoParamGDB
                case 0x20: self.__class__ = TIMonoPolarGDB
                case 0x80: self.__class__ = TIMonoSeqGDB

                case _:
                    warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                         BytesWarning)


class TIGDB(TIMonoGDB):
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

    def coerce(self):
        match self.mode_id:
            case 0x10: self.__class__ = TIFuncGDB
            case 0x40: self.__class__ = TIParamGDB
            case 0x20: self.__class__ = TIPolarGDB
            case 0x80: self.__class__ = TISeqGDB

            case _:
                warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                     BytesWarning)


class TIMonoFuncGDB(TIMonoGDB):
    mode_byte = 0x10

    num_equations = 10
    num_parameters = 1
    num_styles = 10

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, TIReal)[61:70]
    def Xres(self, value: TIReal) -> TIReal:
        """
        Xres: the pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer in [1, 8] for Xres, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, IndexedEquation(1))
    def Y1(self) -> TIGraphedEquation:
        """
        Y1: The first equation in function mode
        """

    @View(data, IndexedEquation(2))
    def Y2(self) -> TIGraphedEquation:
        """
        Y2: The second equation in function mode
        """

    @View(data, IndexedEquation(3))
    def Y3(self) -> TIGraphedEquation:
        """
        Y3: The third equation in function mode
        """

    @View(data, IndexedEquation(4))
    def Y4(self) -> TIGraphedEquation:
        """
        Y4: The fourth equation in function mode
        """

    @View(data, IndexedEquation(5))
    def Y5(self) -> TIGraphedEquation:
        """
        Y5: The fifth equation in function mode
        """

    @View(data, IndexedEquation(6))
    def Y6(self) -> TIGraphedEquation:
        """
        Y6: The sixth equation in function mode
        """

    @View(data, IndexedEquation(7))
    def Y7(self) -> TIGraphedEquation:
        """
        Y7: The seventh equation in function mode
        """

    @View(data, IndexedEquation(8))
    def Y8(self) -> TIGraphedEquation:
        """
        Y8: The eight equation in function mode
        """

    @View(data, IndexedEquation(9))
    def Y9(self) -> TIGraphedEquation:
        """
        Y9: The ninth equation in function mode
        """

    @View(data, IndexedEquation(10))
    def Y0(self) -> TIGraphedEquation:
        """
        Y0: The tenth equation in function mode
        """

    def _load_dict(self, dct: dict):
        for cls in self.__class__.__bases__:
            super(cls, self)._load_dict(dct)


class TIFuncGDB(TIGDB, TIMonoFuncGDB):
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


class TIMonoParamGDB(TIMonoGDB):
    mode_byte = 0x40

    num_equations = 12
    num_parameters = 3
    num_styles = 6

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, TIReal)[61:70]
    def Tmin(self) -> TIReal:
        """
        Tmin: the initial time
        """

    @View(data, TIReal)[70:79]
    def Tmax(self) -> TIReal:
        """
        Tmax: the final time
        """

    @View(data, TIReal)[79:88]
    def Tstep(self) -> TIReal:
        """
        Tstep: the time increment
        """

    @View(data, IndexedEquation(1))
    def X1T(self) -> TIGraphedEquation:
        """
        X1T: The first X-component in parametric mode
        """

    @View(data, IndexedEquation(2))
    def Y1T(self) -> TIGraphedEquation:
        """
        Y1T: The first Y-component in parametric mode
        """

    @View(data, IndexedEquation(3))
    def X2T(self) -> TIGraphedEquation:
        """
        X2T: The second X-component in parametric mode
        """

    @View(data, IndexedEquation(4))
    def Y2T(self) -> TIGraphedEquation:
        """
        Y2T: The second Y-component in parametric mode
        """

    @View(data, IndexedEquation(5))
    def X3T(self) -> TIGraphedEquation:
        """
        X3T: The third X-component in parametric mode
        """

    @View(data, IndexedEquation(6))
    def Y3T(self) -> TIGraphedEquation:
        """
        Y3T: The third Y-component in parametric mode
        """

    @View(data, IndexedEquation(7))
    def X4T(self) -> TIGraphedEquation:
        """
        X4T: The fourth X-component in parametric mode
        """

    @View(data, IndexedEquation(8))
    def Y4T(self) -> TIGraphedEquation:
        """
        Y4T: The fourth Y-component in parametric mode
        """

    @View(data, IndexedEquation(9))
    def X5T(self) -> TIGraphedEquation:
        """
        X5T: The fifth X-component in parametric mode
        """

    @View(data, IndexedEquation(10))
    def Y5T(self) -> TIGraphedEquation:
        """
        Y5T: The fifth Y-component in parametric mode
        """

    @View(data, IndexedEquation(11))
    def X6T(self) -> TIGraphedEquation:
        """
        X6T: The sixth X-component in parametric mode
        """

    @View(data, IndexedEquation(12))
    def Y6T(self) -> TIGraphedEquation:
        """
        Y6T: The sixth Y-component in parametric mode
        """

    def _load_dict(self, dct: dict):
        for i in range(self.num_styles):
            if (x_style := getattr(self, f"X{i}T").style) != (y_style := getattr(self, f"Y{i}T").style):
                warn(f"X and Y component styles do not agree (X{i}T: {x_style}, Y{i}T: {y_style}).",
                     UserWarning)

            if (x_color := getattr(self, f"X{i}T").color) != (y_color := getattr(self, f"Y{i}T").color):
                warn(f"X and Y component colors do not agree (X{i}T: {x_color}, Y{i}T: {y_color}).",
                     UserWarning)


class TIParamGDB(TIGDB, TIMonoParamGDB):
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


class TIMonoPolarGDB(TIMonoGDB):
    mode_byte = 0x20

    num_equations = 6
    num_parameters = 3
    num_styles = 6

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, TIReal)[61:70]
    def Thetamin(self) -> TIReal:
        """
        Thetamin: the initial angle
        """

    @View(data, TIReal)[70:79]
    def Thetamax(self) -> TIReal:
        """
        Thetamax: the final angle
        """

    @View(data, TIReal)[79:88]
    def Thetastep(self) -> TIReal:
        """
        Thetastep: the angle increment
        """

    @View(data, IndexedEquation(1))
    def r1(self) -> TIGraphedEquation:
        """
        r1: The first equation in polar mode
        """

    @View(data, IndexedEquation(2))
    def r2(self) -> TIGraphedEquation:
        """
        r1: The second equation in polar mode
        """

    @View(data, IndexedEquation(3))
    def r3(self) -> TIGraphedEquation:
        """
        r3: The third equation in polar mode
        """

    @View(data, IndexedEquation(4))
    def r4(self) -> TIGraphedEquation:
        """
        rr: The fourth equation in polar mode
        """

    @View(data, IndexedEquation(5))
    def r5(self) -> TIGraphedEquation:
        """
        r5: The fifth equation in polar mode
        """

    @View(data, IndexedEquation(6))
    def r6(self) -> TIGraphedEquation:
        """
        r6: The sixth equation in polar mode
        """


class TIPolarGDB(TIGDB, TIMonoPolarGDB):
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


class TIMonoSeqGDB(TIMonoGDB):
    mode_byte = 0x80

    num_equations = 3
    num_parameters = 10
    num_styles = 3

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, GraphMode)[5:6]
    def sequence_flags(self) -> SeqMode:
        """
        The flags for the sequence mode settings
        """

    @View(data, TIReal)[61:70]
    def PlotStart(self, value) -> TIReal:
        """
        PlotStart: the initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStart, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[70:79]
    def nMax(self, value: TIReal) -> TIReal:
        """
        nMax: the final value of n

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMax, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[79:88]
    def unMin(self) -> TIReal:
        """
        u(nMin): the initial value of u at nMin
        """

    @View(data, TIReal)[88:97]
    def vnMin(self) -> TIReal:
        """
        v(nMin): the initial value of v at nMin
        """

    @View(data, TIReal)[97:106]
    def nMin(self, value: TIReal) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[106:115]
    def unMinp1(self) -> TIReal:
        """
        u(nMin + 1): the initial value of u at nMin + 1
        """

    @View(data, TIReal)[115:124]
    def vnMinp1(self) -> TIReal:
        """
        v(nMin + 1): the initial value of v at nMin + 1
        """

    @View(data, TIReal)[124:133]
    def wnMin(self) -> TIReal:
        """
        w(nMin): the initial value of w at nMin
        """

    @View(data, TIReal)[133:142]
    def PlotStep(self, value: TIReal) -> TIReal:
        """
        PlotStep: the n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStep, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[142:151]
    def wnMinp1(self) -> TIReal:
        """
        w(nMin + 1): the initial value of w at nMin + 1
        """

    @View(data, IndexedEquation(1))
    def u(self) -> TIGraphedEquation:
        """
        u: The first equation in sequence mode
        """

    @View(data, IndexedEquation(2))
    def v(self) -> TIGraphedEquation:
        """
        v: The second equation in sequence mode
        """

    @View(data, IndexedEquation(3))
    def w(self) -> TIGraphedEquation:
        """
        w: The third equation in sequence mode
        """


class TISeqGDB(TIGDB, TIMonoSeqGDB):
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


__all__ = ["TIMonoGDB", "TIMonoFuncGDB", "TIMonoParamGDB", "TIMonoPolarGDB", "TIMonoSeqGDB",
           "TIGDB", "TIFuncGDB", "TIParamGDB", "TIPolarGDB", "TISeqGDB",
           "TIGraphedEquation", "GraphMode", "GraphStyle", "GraphColor", "GlobalStyle"]
