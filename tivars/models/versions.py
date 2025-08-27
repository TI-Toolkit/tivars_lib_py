"""
OS version definitions
"""


import tivars.tokens.scripts as tokens
from .model import *


class OsVersions(tokens.OsVersions):
    """
    Namespace containing useful OS versions

    The maximal elements `OsVersions.INITIAL` and `OsVersions.LATEST` can be accessed via this namespace.
    """

    MATHPRINT = TI_84P.OS("2.53")

    ASMPRGM_DISABLED = TI_84PCE.OS("5.3.1")

    ASM_DISABLED_83PCE = TI_83PCE.OS("5.5.1")
    ASM_DISABLED_84PCETPE = TI_84PCETPE.OS("5.5.5")
    ASM_DISABLED_84PCE = TI_84PCE.OS("5.6.0")

    ARTIFICE_PATCHED = TI_84PCE.OS("5.8.3")
    ARTIFI82_PATCHED = TI_82AEP.OS("5.6.5")


__all__ = ["OsVersions"]
