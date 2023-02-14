from .exact import *
from .fraction import *
from .list import *
from .matrix import *
from .numeric import *
from .tokenized import *
from .window import *

from ..var import TIEntry


# TIEntry.register(TIReal)
# TIEntry.register(TIRealList)
# TIEntry.register(TIMatrix)
TIEntry.register(TIEquation)
TIEntry.register(TIString)
TIEntry.register(TIProgram)
TIEntry.register(TIProtectedProgram)
# TIEntry.register(TIPicture)
# TIEntry.register(TIGraphDatabase)


# TIEntry.register(TISmartEquation)
# TIEntry.register(TIComplex)
# TIEntry.register(TIComplexList)

# TIEntry.register(TIWindowSettings)
# TIEntry.register(TIRecallWindow)
# TIEntry.register(TITableRange)
# TIEntry.register(TIBackup)
# TIEntry.register(TIApp)
# TIEntry.register(TIAppVar)
# TIEntry.register(TIPythonAppVar)
# TIEntry.register(TITemporaryItem)
# TIEntry.register(TIGroup)
# TIEntry.register(TIRealFraction)
# TIEntry.register(TIMixedFraction)
# TIEntry.register(TIImage)
# TIEntry.register(TIExactComplexFraction)
# TIEntry.register(TIExactRealRadical)
# TIEntry.register(TIExactComplexPi)
# TIEntry.register(TIExactComplexPiFraction)
# TIEntry.register(TIExactRealPi)
# TIEntry.register(TIExactRealPiFraction)

# TIEntry.register(TIOperatingSystem)
# TIEntry.register(TIFlashApp)
# TIEntry.register(TICertificate)
# TIEntry.register(TIAppIDList)
# TIEntry.register(TICertificateMemory)

# TIEntry.register(TIClock)

# TIEntry.register(TIFlashLicense)


__all__ = ["TIEntry",
           "TIEquation", "TIString", "TIProgram", "TIProtectedProgram"
           ]
