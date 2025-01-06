"""
Tokenized types
"""


import re

from io import BytesIO
from typing import Iterator, Sequence
from warnings import catch_warnings, simplefilter, warn

from tivars.data import *
from tivars.models import *
from tivars.tokenizer import *
from tivars.var import SizedEntry


class TokenizedEntry(SizedEntry):
    """
    Base class for all tokenized entries

    A tokenized entry is a `SizedEntry` whose data comprises a stream of tokens.
    """

    versions = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
        0x0A, 0x0B, 0x0C,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26,
        0x2A, 0x2B, 0x2C
    ]

    min_data_length = 2

    clock_tokens = [
        b'\xEF\x00', b'\xEF\x01', b'\xEF\x02', b'\xEF\x03', b'\xEF\x04',
        b'\xEF\x07', b'\xEF\x08', b'\xEF\x09', b'\xEF\x0A', b'\xEF\x0B', b'\xEF\x0C', b'\xEF\x0D',
        b'\xEF\x0E', b'\xEF\x0F', b'\xEF\x10'
    ]
    """
    Tokens which interface with the RTC
    
    These tokens influence the entry's version, though detecting the presence of the RTC has no current application.
    """

    def __format__(self, format_spec: str) -> str:
        try:
            lines, sep, spec, lang = re.match(r"(?:(.*?[a-z%#])(\W+))?(\w?)(\.\w+)?$", format_spec).groups()
            lang = (lang or ".en")[1:]

            match spec:
                case "" | "d":
                    string = self.decode(self.data, lang=lang)

                case "a" | "t":
                    string = self.decode(self.data, lang=lang, mode="accessible")

                case _:
                    raise KeyError

            if lines:
                return "\n".join(f"{index:{lines}}{sep}" + line for index, line in enumerate(string.split("\n")))

            else:
                return string

        except (AttributeError, KeyError, TypeError, ValueError):
            return super().__format__(format_spec)

    def __iter__(self) -> Iterator[TIToken]:
        return iter(self.tokens())

    @staticmethod
    def decode(data: bytes, *, model: TIModel = None, lang: str = None, mode: str = None) -> str:
        """
        Decodes a byte stream into a string of tokens

        :param data: The token bytes to decode
        :param model: A model for which compatibility is ensured (defaults to the TI-84+CE)
        :param lang: The language used in ``string`` (defaults to the locale of `model`, or English, ``en``)
        :param mode: The form of token representation to use for output (defaults to ``display``)
        :return: A string of token representations
        """

        try:
            model = model or TI_84PCE
            return "".join(getattr(token.langs[lang or model.lang], mode or "display")
                           for token in decode(data, tokens=model.tokens)[0])

        except (AttributeError, TypeError):
            raise ValueError(f"unrecognized tokenization mode: '{mode}'")

    @staticmethod
    def encode(string: str, *, model: TIModel = None, lang: str = None, mode: str = None) -> bytes:
        """
        Encodes a string of token represented in text into a byte stream

        For detailed information on tokenization modes, see `tivars.tokenizer.encode`.

        :param string: The text string to encode
        :param model: A model to target when encoding (defaults to no specific model)
        :param lang: The language used in ``string`` (defaults to the locale of `model`, or English, ``en``)
        :param mode: The tokenization mode to use (defaults to ``smart``)
        :return: A stream of token bytes
        """

        model = model or TI_84PCE
        return encode(string, trie=model.tokens.tries[lang or model.lang], mode=mode)[0]

    def get_min_os(self, data: bytes = None) -> OsVersion:
        return decode(data or self.data)[1]

    def get_version(self, data: bytes = None) -> int:
        match self.get_min_os(data):
            case os if os >= TI_84PCE.OS("5.3"):
                version = 0x0C

            case os if os >= TI_84PCE.OS("5.2"):
                version = 0x0B

            case os if os >= TI_84PCSE.OS("4.0"):
                version = 0x0A

            case os if os >= TI_84P.OS("2.55"):
                version = 0x07

            case os if os >= TI_84P.OS("2.53"):
                version = 0x06

            case os if os >= TI_84P.OS("2.30"):
                version = 0x05

            case os if os >= TI_84P.OS("2.21"):
                version = 0x04

            case os if os >= TI_83P.OS("1.16"):
                version = 0x03

            case os if os >= TI_83P.OS("1.15"):
                version = 0x02

            case os if os >= TI_83P.OS("1.00"):
                version = 0x01

            case _:
                version = 0x00

        if any(token in (data or self.data) for token in self.clock_tokens):
            version += 0x20

        return version

    @Loader[bytes, bytearray, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super().load_bytes(data)

        try:
            if self.version != (version := self.get_version()):
                warn(f"The version is incorrect (expected 0x{version:02x}, got 0x{self.version:02x}).",
                     BytesWarning)

        except ValueError as e:
            warn(f"The file contains an invalid token {' '.join(str(e).split()[2:])}.",
                 BytesWarning)

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None, lang: str = None, mode: str = None):
        """
        Loads this entry from a string representation

        For detailed information on tokenization modes, see `tivars.tokenizer.encode`.

        :param string: The string to load
        :param model: The model to target when encoding (defaults to no specific model)
        :param lang: The language used in ``string`` (defaults to English, ``en``)
        :param mode: The tokenization mode to use (defaults to ``smart``)
        """

        self.data = self.encode(string, model=model, lang=lang, mode=mode)

    @Loader[Sequence[TIToken]]
    def load_tokens(self, tokens: Sequence[TIToken]):
        """
        Loads this entry from a sequence of `TIToken` objects

        :param tokens: The sequence of tokens to load
        """

        self.data = b''.join(token.bits for token in tokens)

    def tokens(self) -> list[TIToken]:
        """
        :return: The tokens comprising this entry as a list of `TIToken` objects
        """

        return decode(self.data)[0]

    def lines(self) -> list[list[TIToken]]:
        """
        Splits this entry into logical lines: lines separated by newlines or colons lying outside string literals

        This method is *not* used to format entries with line numbers; only literal newlines are considered there.
        To split on just literal newlines or some other separator, use ``.string().split``.

        :return: The logical lines of this entry as lists of `TIToken` objects
        """

        tokens = self.tokens()
        lines = [[]]

        in_string = False
        for token in tokens:
            match token.bits:
                #    ->
                case b'\x04':
                    in_string = False

                #    "
                case b'\x2A':
                    in_string = not in_string

                #    :
                case b'\x3E' if not in_string:
                    lines.append([])

                #    \n
                case b'\x3F':
                    in_string = False
                    lines.append([])

                case _:
                    lines[-1].append(token)

        return lines


class TIEquation(TokenizedEntry, register=True):
    """
    Parser for equations

    A `TIEquation` is a stream of tokens that is evaluated either for graphing or on the homescreen.
    """

    extensions = {
        None: "8xy",
        TI_82: "82y",
        TI_83: "83y",
        TI_83P: "8xy"
    }

    leading_name_byte = b'\x5E'

    _type_id = 0x03

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Y1",
                 version: int = None, archived: bool = None,
                 data: bytes = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, Name)
    def name(self, value) -> str:
        """
        The name of the entry

        Must be an equation name used in function, parametric, polar, or sequence mode.
        (See https://ti-toolkit.github.io/tokens-wiki/categories/Y%3D%20Functions.html)
        """

        varname = value
        if varname in ("u", "v", "w"):
            varname = "|" + varname

        elif match := re.fullmatch(r"\{?([XYr]\dT?)}?", varname):
            varname = "{" + match[1] + "}"

        return varname


class TINewEquation(TIEquation, register=True):
    """
    Parser for internal equations

    A `TINewEquation` is simply a `TIEquation` with certain internal uses.
    """

    _type_id = 0x0B


class TIString(TokenizedEntry, register=True):
    """
    Parser for strings

    A `TIString` is a stream of tokens.
    """

    extensions = {
        None: "8xs",
        TI_82: "82s",
        TI_83: "83s",
        TI_83P: "8xs"
    }

    leading_name_byte = b'\xAA'

    _type_id = 0x04

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "Str1",
                 version: int = None, archived: bool = None,
                 data: bytes = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @Section(8, Name)
    def name(self, value) -> str:
        """
        The name of the entry

        Must be one of the string names: ``Str1`` - ``Str0``.
        """

        return value.capitalize()

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None, lang: str = None, mode: str = None):
        super().load_string(string.strip("\""), model=model, lang=lang, mode=mode)

    def string(self) -> str:
        return f"\"{super().string()}\""


class TIProgram(TokenizedEntry, register=True):
    """
    Parser for programs

    A `TIProgram` is a stream of tokens that is run as a TI-BASIC program.
    """

    extensions = {
        None: "8xp",
        TI_82: "82p",
        TI_83: "83p",
        TI_83P: "8xp"
    }

    is_protected = False
    """
    Whether this program type is protected
    """

    is_tokenized = True
    """
    Whether this program is tokenized
    """

    asm_tokens = {b'\xBB\x6D': TI_83P,
                  b'\xEF\x69': TI_84PCSE,
                  b'\xEF\x7B': TI_84PCE}
    """
    Tokens which identify the program as containing assembly code
    """

    _type_id = 0x05

    def protect(self):
        """
        Cast this program to a protected program
        """

        self.type_id = TIProtectedProgram.type_id
        self.coerce()

    def unprotect(self):
        """
        Cast this program to an unprotected program
        """

        self.type_id = TIProgram.type_id
        self.coerce()

    @Loader[bytes, bytearray, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        super(TokenizedEntry, self).load_bytes(data)

        if self.is_tokenized:
            try:
                if self.version != (version := self.get_version()):
                    warn(f"The version is incorrect (expected 0x{version:02x}, got 0x{self.version:02x}).",
                         BytesWarning)

            except ValueError as e:
                warn(f"The file contains an invalid token {' '.join(str(e).split()[2:])}.",
                     BytesWarning)

    @Loader[str]
    def load_string(self, string: str, *, model: TIModel = None, lang: str = None, mode: str = None):
        if not self.is_tokenized:
            warn("ASM programs may not have tokenized data.",
                 UserWarning)

        super().load_string(string, model=model, lang=lang, mode=mode)

    def string(self) -> str:
        if not self.is_tokenized:
            warn("ASM programs may not have tokenized data.",
                 UserWarning)

            with catch_warnings():
                simplefilter("ignore")
                return super().string()

        else:
            return super().string()

    def coerce(self):
        with catch_warnings():
            simplefilter("error")

            try:
                self.string()
                doors = False

            except BytesWarning:
                doors = True

        doors &= b"\xEF\x68" in self.data and self.data.index(b"\xEF\x68") > 0

        match self.type_id, any(token in self.data for token in self.asm_tokens) | doors:
            case TIProgram.type_id, False:
                self.__class__ = TIProgram
            case TIProgram.type_id, True:
                self.__class__ = TIAsmProgram
            case TIProtectedProgram.type_id, False:
                self.__class__ = TIProtectedProgram
            case TIProtectedProgram.type_id, True:
                self.__class__ = TIProtectedAsmProgram


class TIAsmProgram(TIProgram):
    """
    Parser for assembly programs

    A `TIAsmProgram` is a stream of raw bytes that is run as assembly code.
    A single valid token at the start of the data section identifies the program as using assembly.

    A consistent method of ASM identification for the TI-83 is not yet implemented.
    """

    is_tokenized = False

    def get_min_os(self, data: bytes = None) -> OsVersion:
        return max([model.OS() for token, model in self.asm_tokens.items() if token in (data or self.data)],
                   default=OsVersions.INITIAL)


class TIProtectedProgram(TIProgram, register=True):
    """
    Parser for protected programs

    A `TIProtectedProgram` is a `TIProgram` with protection against editing.
    """

    is_protected = True

    _type_id = 0x06


class TIProtectedAsmProgram(TIAsmProgram, TIProtectedProgram):
    """
    Parser for protected assembly programs

    A `TIProtectedAsmProgram` is a `TIAsmProgram` with protection against editing.
    """

    is_protected = True

    _type_id = 0x06


__all__ = ["TIEquation", "TINewEquation", "TIString",
           "TIProgram", "TIAsmProgram", "TIProtectedProgram", "TIProtectedAsmProgram"]
