import json

from io import BytesIO
from typing import ByteString
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .real import GraphRealEntry


class SettingsEntry(TIEntry):
    """
    Base class for settings entries

    A settings entry stores all parameters for the different plot windows or tables
    """

    min_data_length = 2

    leading_bytes = b''

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Window",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Loader[ByteString, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        if self.data[:len(self.leading_bytes)] != self.leading_bytes:
            warn(f"The entry has unexpected leading bytes "
                 f"(expected {self.leading_bytes}, got {self.data[:len(self.leading_bytes)]}).",
                 BytesWarning)

    @Loader[dict]
    def load_dict(self, dct: dict):
        """
        Loads a JSON `dict` into this settings entry

        :param dct: The dict to load
        """

        for var, value in dct:
            if not hasattr(self, var):
                warn(f"Unrecognized window setting ({var}).",
                     UserWarning)
            else:
                setattr(self, var, GraphRealEntry(value))

    def dict(self) -> dict:
        """
        :return: A `dict` representing this settings entry in JSON format
        """

        raise NotImplementedError

    @Loader[str]
    def load_string(self, string: str):
        self.load_dict(json.loads(string))

    def string(self) -> str:
        return json.dumps(self.dict())


class TIWindowSettings(SettingsEntry, register=True):
    """
    Parser for window settings

    A `TIWindowSettings` stores all plot window parameters as a contiguous stream of `TIReal` values.
    """

    extensions = {
        None: "8xw",
        TI_82: "82w",
        TI_83: "83w",
        TI_82A: "8xw",
        TI_82P: "8xw",
        TI_83P: "8xw",
        TI_84P: "8xw",
        TI_84T: "8xw",
        TI_84PCSE: "8xw",
        TI_84PCE: "8xw",
        TI_84PCEPY: "8xw",
        TI_83PCE: "8xw",
        TI_83PCEEP: "8xw",
        TI_82AEP: "8xw"
    }

    min_data_length = 210

    _type_id = 0x0F
    leading_bytes = b'\xD0\x00\x00'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Window",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, String)
    def name(self) -> str:
        pass

    @Section(min_data_length)
    def data(self) -> bytearray:
        pass

    @View(data, GraphRealEntry)[3:12]
    def Xmin(self) -> GraphRealEntry:
        """
        Xmin: the X-coordinate of the left edge of the graphscreen
        """

    @View(data, GraphRealEntry)[12:21]
    def Xmax(self) -> GraphRealEntry:
        """
        Xmax: the X-coordinate of the right edge of the graphscreen
        """

    @View(data, GraphRealEntry)[21:30]
    def Xscl(self) -> GraphRealEntry:
        """
        Xscl: the separation between ticks on the X-axis
        """

    @View(data, GraphRealEntry)[30:39]
    def Ymin(self) -> GraphRealEntry:
        """
        Ymin: the Y-coordinate of the bottom edge of the graphscreen
        """

    @View(data, GraphRealEntry)[39:48]
    def Ymax(self) -> GraphRealEntry:
        """
        Ymax: the Y-coordinate of the top edge of the graphscreen
        """

    @View(data, GraphRealEntry)[48:57]
    def Yscl(self) -> GraphRealEntry:
        """
        Yscl: the separation between ticks on the Y-axis
        """

    @View(data, GraphRealEntry)[57:66]
    def Thetamin(self) -> GraphRealEntry:
        """
        Θmin: the initial angle for polar plots
        """

    @View(data, GraphRealEntry)[66:75]
    def Thetamax(self) -> GraphRealEntry:
        """
        Θmax: the final angle for polar plots
        """

    @View(data, GraphRealEntry)[75:84]
    def Thetastep(self) -> GraphRealEntry:
        """
        Θstep: the angle increment for polar plots
        """

    @View(data, GraphRealEntry)[84:93]
    def Tmin(self) -> GraphRealEntry:
        """
        Tmin: the initial time for parametric plots
        """

    @View(data, GraphRealEntry)[93:102]
    def Tmax(self) -> GraphRealEntry:
        """
        Tmax: the final time for parametric plots
        """

    @View(data, GraphRealEntry)[102:111]
    def Tstep(self) -> GraphRealEntry:
        """
        Tstep: the time increment for parametric plots
        """

    @View(data, GraphRealEntry)[111:120]
    def PlotStart(self, value) -> GraphRealEntry:
        """
        PlotStart: the initial value of 𝑛 for sequential plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[120:129]
    def nMax(self, value) -> GraphRealEntry:
        """
        𝑛Max: the final value of 𝑛 for sequential equations and plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[129:138]
    def unMin0(self) -> GraphRealEntry:
        """
        u(𝑛Min): the initial value of u at 𝑛Min
        """

    @View(data, GraphRealEntry)[138:147]
    def vnMin0(self) -> GraphRealEntry:
        """
        v(𝑛Min): the initial value of v at 𝑛Min
        """

    @View(data, GraphRealEntry)[147:156]
    def nMin(self, value) -> GraphRealEntry:
        """
        𝑛Min: the initial value of 𝑛 for sequential plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[156:165]
    def unMin1(self) -> GraphRealEntry:
        """
        u(𝑛Min+1): the initial value of u at 𝑛Min + 1
        """

    @View(data, GraphRealEntry)[165:174]
    def vnMin1(self) -> GraphRealEntry:
        """
        v(𝑛Min+1): the initial value of v at 𝑛Min + 1
        """

    @View(data, GraphRealEntry)[174:183]
    def wnMin0(self) -> GraphRealEntry:
        """
        w(𝑛Min): the initial value of w at 𝑛Min
        """

    @View(data, GraphRealEntry)[183:192]
    def PlotStep(self, value) -> GraphRealEntry:
        """
        PlotStep: the 𝑛 increment for sequential plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[192:201]
    def Xres(self, value) -> GraphRealEntry:
        """
        Xres: the pixel separation of points in a function plot

        The value must be an integer in [1,8]
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer between 1 and 8, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[201:210]
    def wnMin1(self) -> GraphRealEntry:
        """
        w(𝑛Min+1): the initial value of w at 𝑛Min + 1
        """

    def dict(self) -> dict:
        return {
            "Xmin": self.Xmin.json_number(),
            "Xmax": self.Xmax.json_number(),
            "Xscl": self.Xscl.json_number(),
            "Ymin": self.Ymin.json_number(),
            "Ymax": self.Ymax.json_number(),
            "Yscl": self.Yscl.json_number(),
            "Thetamin": self.Thetamin.json_number(),
            "Thetamax": self.Thetamax.json_number(),
            "Thetastep": self.Thetastep.json_number(),
            "Tmin": self.Tmin.json_number(),
            "Tmax": self.Tmax.json_number(),
            "Tstep": self.Tstep.json_number(),
            "PlotStart": int(self.PlotStart),
            "nMax": int(self.nMax),
            "unMin0": self.unMin0.json_number(),
            "vnMin0": self.vnMin0.json_number(),
            "nMin": int(self.nMin),
            "unMin1": self.unMin1.json_number(),
            "vnMin1": self.vnMin1.json_number(),
            "wnMin0": self.wnMin0.json_number(),
            "PlotStep": int(self.PlotStep),
            "Xres": int(self.Xres),
            "wnMin1": self.wnMin1.json_number()
        }


class TIRecallWindow(SettingsEntry, register=True):
    """
    Parser for recalled windows

    A `TIRecallWindow` stores all plot window parameters as a contiguous stream of `TIReal` values.
    """

    extensions = {
        None: "8xz",
        TI_82: "82z",
        TI_83: "83z",
        TI_82A: "8xz",
        TI_82P: "8xz",
        TI_83P: "8xz",
        TI_84P: "8xz",
        TI_84T: "8xz",
        TI_84PCSE: "8xz",
        TI_84PCE: "8xz",
        TI_84PCEPY: "8xz",
        TI_83PCE: "8xz",
        TI_83PCEEP: "8xz",
        TI_82AEP: "8xz"
    }

    min_data_length = 209

    _type_id = 0x10
    leading_bytes = b'\xCF\x00'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "RclWindw",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, String)
    def name(self) -> str:
        """
        The name of the entry

        Always equal to RclWindw.
        """

    @Section(min_data_length)
    def data(self) -> bytearray:
        pass

    @View(data, GraphRealEntry)[2:11]
    def Xmin(self) -> GraphRealEntry:
        """
        Xmin: the X-coordinate of the left edge of the graphscreen
        """

    @View(data, GraphRealEntry)[11:20]
    def Xmax(self) -> GraphRealEntry:
        """
        Xmax: the X-coordinate of the right edge of the graphscreen
        """

    @View(data, GraphRealEntry)[20:29]
    def Xscl(self) -> GraphRealEntry:
        """
        Xscl: the separation between ticks on the X-axis
        """

    @View(data, GraphRealEntry)[29:38]
    def Ymin(self) -> GraphRealEntry:
        """
        Ymin: the Y-coordinate of the bottom edge of the graphscreen
        """

    @View(data, GraphRealEntry)[38:47]
    def Ymax(self) -> GraphRealEntry:
        """
        Ymax: the Y-coordinate of the top edge of the graphscreen
        """

    @View(data, GraphRealEntry)[47:56]
    def Yscl(self) -> GraphRealEntry:
        """
        Yscl: the separation between ticks on the Y-axis
        """

    @View(data, GraphRealEntry)[56:65]
    def Thetamin(self) -> GraphRealEntry:
        """
        Θmin: the initial angle for polar plots
        """

    @View(data, GraphRealEntry)[65:74]
    def Thetamax(self) -> GraphRealEntry:
        """
        Θmax: the final angle for polar plots
        """

    @View(data, GraphRealEntry)[74:83]
    def Thetastep(self) -> GraphRealEntry:
        """
        Θstep: the angle increment for polar plots
        """

    @View(data, GraphRealEntry)[83:92]
    def Tmin(self) -> GraphRealEntry:
        """
        Tmin: the initial time for parametric plots
        """

    @View(data, GraphRealEntry)[92:101]
    def Tmax(self) -> GraphRealEntry:
        """
        Tmax: the final time for parametric plots
        """

    @View(data, GraphRealEntry)[101:110]
    def Tstep(self) -> GraphRealEntry:
        """
        Tstep: the time increment for parametric plots
        """

    @View(data, GraphRealEntry)[110:119]
    def PlotStart(self, value) -> GraphRealEntry:
        """
        PlotStart: the initial value of 𝑛 for sequential plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[119:128]
    def nMax(self, value) -> GraphRealEntry:
        """
        𝑛Max: the final value of 𝑛 for sequential equations and plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[128:137]
    def unMin0(self) -> GraphRealEntry:
        """
        u(𝑛Min): the initial value of u at 𝑛Min
        """

    @View(data, GraphRealEntry)[137:146]
    def vnMin0(self) -> GraphRealEntry:
        """
        v(𝑛Min): the initial value of v at 𝑛Min
        """

    @View(data, GraphRealEntry)[146:155]
    def nMin(self, value) -> GraphRealEntry:
        """
        𝑛Min: the initial value of 𝑛 for sequential equations

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[155:164]
    def unMin1(self) -> GraphRealEntry:
        """
        u(𝑛Min + 1): the initial value of u at 𝑛Min + 1
        """

    @View(data, GraphRealEntry)[164:173]
    def vnMin1(self) -> GraphRealEntry:
        """
        v(𝑛Min + 1): the initial value of v at 𝑛Min + 1
        """

    @View(data, GraphRealEntry)[173:182]
    def wnMin0(self) -> GraphRealEntry:
        """
        w(𝑛Min): the initial value of w at 𝑛Min
        """

    @View(data, GraphRealEntry)[182:191]
    def PlotStep(self, value) -> GraphRealEntry:
        """
        PlotStep: the 𝑛 increment for sequential plots

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[191:200]
    def Xres(self, value) -> GraphRealEntry:
        """
        Xres: the pixel separation of points in a function plot

        The value must be an integer in [1,8]
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer between 1 and 8, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[200:209]
    def wnMin1(self) -> GraphRealEntry:
        """
        w(𝑛Min + 1): the initial value of w at 𝑛Min + 1
        """

    def dict(self) -> dict:
        return {
            "Xmin": self.Xmin.json_number(),
            "Xmax": self.Xmax.json_number(),
            "Xscl": self.Xscl.json_number(),
            "Ymin": self.Ymin.json_number(),
            "Ymax": self.Ymax.json_number(),
            "Yscl": self.Yscl.json_number(),
            "Thetamin": self.Thetamin.json_number(),
            "Thetamax": self.Thetamax.json_number(),
            "Thetastep": self.Thetastep.json_number(),
            "Tmin": self.Tmin.json_number(),
            "Tmax": self.Tmax.json_number(),
            "Tstep": self.Tstep.json_number(),
            "PlotStart": int(self.PlotStart),
            "nMax": int(self.nMax),
            "unMin0": self.unMin0.json_number(),
            "vnMin0": self.vnMin0.json_number(),
            "nMin": int(self.nMin),
            "unMin1": self.unMin1.json_number(),
            "vnMin1": self.vnMin1.json_number(),
            "wnMin0": self.wnMin0.json_number(),
            "PlotStep": int(self.PlotStep),
            "Xres": int(self.Xres),
            "wnMin1": self.wnMin1.json_number()
        }


class TITableSettings(SettingsEntry, register=True):
    """
    Parser for table settings

    A `TITableSettings` stores all plot table parameters as a contiguous stream of `TIReal` values.
    """

    extensions = {
        None: "8xt",
        TI_82: "82t",
        TI_83: "83t",
        TI_82A: "8xt",
        TI_82P: "8xt",
        TI_83P: "8xt",
        TI_84P: "8xt",
        TI_84T: "8xt",
        TI_84PCSE: "8xt",
        TI_84PCE: "8xt",
        TI_84PCEPY: "8xt",
        TI_83PCE: "8xt",
        TI_83PCEEP: "8xt",
        TI_82AEP: "8xt"
    }

    min_data_length = 20

    _type_id = 0x11
    leading_bytes = b'\x12\x00'

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "TblSet",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, String)
    def name(self) -> str:
        """
        The name of the entry

        Always equal to TblSet.
        """

    @Section(min_data_length)
    def data(self) -> bytearray:
        pass

    @View(data, GraphRealEntry)[2:11]
    def TblMin(self, value) -> GraphRealEntry:
        """
        TblMin: the initial value for the table

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer for TblMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphRealEntry)[11:20]
    def DeltaTbl(self, value) -> GraphRealEntry:
        """
        ΔTbl: the increment for the table

        The value must be an integer.
        """

        if int(value) != float(value):
            warn(f"Expected an integer for ΔTbl, got {float(value)}.",
                 UserWarning)

        return value

    def dict(self) -> dict:
        return {
            "TblMin": int(self.TblMin),
            "DeltaTbl": int(self.DeltaTbl)
        }


__all__ = ["TIWindowSettings", "TIRecallWindow", "TITableSettings"]
