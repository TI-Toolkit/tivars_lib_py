from .tokenized import *

from ..var import TIVar


TIVar.register(TIEquation)
TIVar.register(TIString)
TIVar.register(TIProgram)
TIVar.register(TIProtectedProgram)


__all__ = ["TIVar", "TIEquation", "TIString", "TIProgram", "TIProtectedProgram"]
