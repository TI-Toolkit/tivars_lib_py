from .tokenized import *

from ..var import TIEntry


TIEntry.register(TIEquation)
TIEntry.register(TIString)
TIEntry.register(TIProgram)
TIEntry.register(TIProtectedProgram)


__all__ = ["TIEntry", "TIEquation", "TIString", "TIProgram", "TIProtectedProgram"]
