import json

from io import BytesIO
from typing import ByteString
from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal


class SettingsEntry(TIEntry):
    min_data_length = 2

    leading_bytes = b''

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Window",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.raw.data[:len(self.leading_bytes)] = self.leading_bytes

    @Loader[ByteString, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        if self.data[:len(self.leading_bytes)] != self.leading_bytes:
            warn(f"The entry has unexpected leading bytes "
                 f"(expected {self.leading_bytes}, got {self.data[:len(self.leading_bytes)]}).",
                 BytesWarning)

    @Loader[dict]
    def load_dict(self, dct: dict):
        for var, value in dct:
            if not hasattr(self, var):
                warn(f"Unrecognized window setting ({var}).",
                     UserWarning)
            else:
                setattr(self, var, TIReal(value))

    def dict(self) -> dict:
        raise NotImplementedError

    @Loader[str]
    def load_string(self, string: str):
        self.load_dict(json.loads(string))

    def string(self) -> str:
        return json.dumps(self.dict())


class TIWindowSettings(SettingsEntry):
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

    _type_id = b'\x0F'
    leading_bytes = b'\xD0\x00\x00'

    @Section(8, String)
    def name(self) -> str:
        """
        The name of the entry

        Always equal to Window
        """

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the window parameter values
        """

    @View(data, TIReal)[3:12]
    def Xmin(self) -> TIReal:
        """
        Xmin: the smallest or leftmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[12:21]
    def Xmax(self) -> TIReal:
        """
        Xmax: the largest or rightmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[21:30]
    def Xscl(self) -> TIReal:
        """
        Xscl: the separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[30:39]
    def Ymin(self) -> TIReal:
        """
        Ymin: the smallest or bottommost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[39:48]
    def Ymax(self) -> TIReal:
        """
        Ymax: the largest or topmost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[48:57]
    def Yscl(self) -> TIReal:
        """
        Yscl: the separation between ticks on the vertical axis
        """

    @View(data, TIReal)[57:66]
    def Thetamin(self) -> TIReal:
        """
        Θmin: the initial angle for polar plots
        """

    @View(data, TIReal)[66:75]
    def Thetamax(self) -> TIReal:
        """
        Θmax: the final angle for polar plots
        """

    @View(data, TIReal)[75:84]
    def Thetastep(self) -> TIReal:
        """
        Θstep: the angle increment for polar plots
        """

    @View(data, TIReal)[84:93]
    def Tmin(self) -> TIReal:
        """
        Tmin: the initial time for parametric plots
        """

    @View(data, TIReal)[93:102]
    def Tmax(self) -> TIReal:
        """
        Tmax: the final time for parametric plots
        """

    @View(data, TIReal)[102:111]
    def Tstep(self) -> TIReal:
        """
        Tstep: the time increment for parametric plots
        """

    @View(data, TIReal)[111:120]
    def PlotStart(self, value) -> TIReal:
        """
        PlotStart: the initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[120:129]
    def nMax(self, value) -> TIReal:
        """
        nMax: the final value of n for sequential equations and plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[129:138]
    def unMin0(self) -> TIReal:
        """
        u(nMin): the initial value of u at nMin
        """

    @View(data, TIReal)[138:147]
    def vnMin0(self) -> TIReal:
        """
        v(nMin): the initial value of v at nMin
        """

    @View(data, TIReal)[147:156]
    def nMin(self, value) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[156:165]
    def unMin1(self) -> TIReal:
        """
        u(nMin + 1): the initial value of u at nMin + 1
        """

    @View(data, TIReal)[165:174]
    def vnMin1(self) -> TIReal:
        """
        v(nMin + 1): the initial value of v at nMin + 1
        """

    @View(data, TIReal)[174:183]
    def wnMin0(self) -> TIReal:
        """
        w(nMin): the initial value of w at nMin
        """

    @View(data, TIReal)[183:192]
    def PlotStep(self, value) -> TIReal:
        """
        PlotStep: the n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[192:201]
    def Xres(self, value) -> TIReal:
        """
        Xres: the pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer between 1 and 8, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[201:210]
    def wnMin1(self) -> TIReal:
        """
        w(nMin + 1): the initial value of w at nMin + 1
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


class TIRecallWindow(SettingsEntry):
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

    _type_id = b'\x10'
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

        Always equal to RclWindw
        """

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the window parameter values
        """

    @View(data, TIReal)[2:11]
    def Xmin(self) -> TIReal:
        """
        Xmin: the smallest or leftmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[11:20]
    def Xmax(self) -> TIReal:
        """
        Xmax: the largest or rightmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[20:29]
    def Xscl(self) -> TIReal:
        """
        Xscl: the separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[29:38]
    def Ymin(self) -> TIReal:
        """
        Ymin: the smallest or bottommost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[38:47]
    def Ymax(self) -> TIReal:
        """
        Ymax: the largest or topmost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[47:56]
    def Yscl(self) -> TIReal:
        """
        Yscl: the separation between ticks on the vertical axis
        """

    @View(data, TIReal)[56:65]
    def Thetamin(self) -> TIReal:
        """
        Θmin: the initial angle for polar plots
        """

    @View(data, TIReal)[65:74]
    def Thetamax(self) -> TIReal:
        """
        Θmax: the final angle for polar plots
        """

    @View(data, TIReal)[74:83]
    def Thetastep(self) -> TIReal:
        """
        Θstep: the angle increment for polar plots
        """

    @View(data, TIReal)[83:92]
    def Tmin(self) -> TIReal:
        """
        Tmin: the initial time for parametric plots
        """

    @View(data, TIReal)[92:101]
    def Tmax(self) -> TIReal:
        """
        Tmax: the final time for parametric plots
        """

    @View(data, TIReal)[101:110]
    def Tstep(self) -> TIReal:
        """
        Tstep: the time increment for parametric plots
        """

    @View(data, TIReal)[110:119]
    def PlotStart(self, value) -> TIReal:
        """
        PlotStart: the initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[119:128]
    def nMax(self, value) -> TIReal:
        """
        nMax: the final value of n for sequential equations and plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[128:137]
    def unMin0(self) -> TIReal:
        """
        u(nMin): the initial value of u at nMin
        """

    @View(data, TIReal)[137:146]
    def vnMin0(self) -> TIReal:
        """
        v(nMin): the initial value of v at nMin
        """

    @View(data, TIReal)[146:155]
    def nMin(self, value) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[155:164]
    def unMin1(self) -> TIReal:
        """
        u(nMin + 1): the initial value of u at nMin + 1
        """

    @View(data, TIReal)[164:173]
    def vnMin1(self) -> TIReal:
        """
        v(nMin + 1): the initial value of v at nMin + 1
        """

    @View(data, TIReal)[173:182]
    def wnMin0(self) -> TIReal:
        """
        w(nMin): the initial value of w at nMin
        """

    @View(data, TIReal)[182:191]
    def PlotStep(self, value) -> TIReal:
        """
        PlotStep: the n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[191:200]
    def Xres(self, value) -> TIReal:
        """
        Xres: the pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer between 1 and 8, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[200:209]
    def wnMin1(self) -> TIReal:
        """
        w(nMin + 1): the initial value of w at nMin + 1
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


class TITableSettings(SettingsEntry):
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

    _type_id = b'\x11'
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

        Always equal to TblSet
        """

    @Section(min_data_length)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the table parameter values
        """

    @View(data, TIReal)[2:11]
    def TblMin(self, value) -> TIReal:
        """
        TblMin: the initial value for the table

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for TblMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[11:20]
    def DeltaTbl(self, value) -> TIReal:
        """
        ΔTbl: the increment for the table

        Must be an integer
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
