class TIModel:
    def __init__(self, name: str, flags: int, signature: str):
        self.name = name
        self.flags = flags
        self.signature = signature.encode('utf8')

    def has(self, feature: int):
        return self.flags & feature


class TIFeatures:
    NONE = 0
    DEFAULT = 1 << 0
    COMPLEX = 1 << 1
    FLASH = 1 << 2
    APPS = 1 << 3
    CLOCK = 1 << 4
    COLOR = 1 << 5
    EZ80 = 1 << 6
    EXACT_MATH = 1 << 7
    PYTHON = 1 << 8


features = [TIFeatures.NONE, TIFeatures.DEFAULT, TIFeatures.COMPLEX, TIFeatures.FLASH, TIFeatures.APPS,
            TIFeatures.CLOCK, TIFeatures.COLOR, TIFeatures.EZ80, TIFeatures.EXACT_MATH, TIFeatures.PYTHON]


flags82 = 0 | TIFeatures.DEFAULT
flags83 = flags82 | TIFeatures.COMPLEX
flags82a = flags83 | TIFeatures.FLASH
flags83p = flags82a | TIFeatures.APPS
flags84p = flags83p | TIFeatures.CLOCK
flags84pcse = flags84p | TIFeatures.COLOR
flags84pce = flags84pcse | TIFeatures.EZ80
flags83pce = flags84pce | TIFeatures.EXACT_MATH
flags83pceep = flags83pce | TIFeatures.PYTHON
flags84pcepy = flags84pce | TIFeatures.PYTHON
flags82aep = flags83pceep & ~TIFeatures.APPS

TI_82 = TIModel("82", flags82, "**TI82**")
TI_83 = TIModel("83", flags83, "**TI83**")
TI_82a = TIModel("82A", flags82a, "**TI83F*")
TI_82p = TIModel("82+", flags83p, "**TI83F*")
TI_83p = TIModel("83+", flags83p, "**TI83F*")
TI_84p = TIModel("84+", flags84p, "**TI83F*")
TI_84t = TIModel("84+T", flags84p, "**TI83F*")
TI_84pcse = TIModel("84+CSE", flags84pcse, "**TI83F*")
TI_84pce = TIModel("84+CE", flags84pce, "**TI83F*")
TI_84pcet = TIModel("84+CET", flags84pce, "**TI83F*")
TI_84pcetpy = TIModel("84+CETPE", flags84pcepy, "**TI83F*")
TI_84pcepy = TIModel("84+CEPy", flags84pcepy, "**TI83F*")
TI_83pce = TIModel("83PCE", flags83pce, "**TI83F*")
TI_83pceep = TIModel("83PCEEP", flags83pceep, "**TI83F*")
TI_82aep = TIModel("82AEP", flags82aep, "**TI83F*")

models = [TI_82, TI_83, TI_82a, TI_82p, TI_83p,
          TI_84p, TI_84t, TI_84pcse, TI_84pce, TI_84pcet, TI_84pcetpy, TI_84pcepy,
          TI_83pce, TI_83pceep, TI_82aep]


__all__ = ["TI_82", "TI_83", "TI_82a", "TI_83p",
           "TI_84p", "TI_84t", "TI_84pcse", "TI_84pce", "TI_83pce", "TI_84pcet", "TI_84pcetpy", "TI_84pcepy",
           "TI_83pce", "TI_83pceep", "TI_82aep",
           "models", "TIFeatures", "features", "TIModel"]
