"""
NFA implementation for context-aware tokenization with lookahead
"""


from string import punctuation

from tivars.token import *
from tivars.trie import *


class TokenizerState:
    """
    Base class for tokenizer states

    Each state represents some encoding context which affects tokenization.
    """

    max_length: int = None
    """
    The maximum number of tokens to emit before leaving this state
    """

    def __init__(self, mode: int, accept: bool = True, length: int = 0):
        """
        :param mode: Whether to munch maximally (``0``) or minimally (``-1``)
        :param accept: Whether this state can end a timeline (defaults to ``True``)
        :param length: The current length of the input this state is going to process (defaults to ``0``)
        """

        self.mode = mode
        self.accept = accept
        self.length = length

    def munch(self, string: str, trie: TITokenTrie) -> tuple[TIToken, str, list[list['TokenizerState']]]:
        """
        Munch the input string and determine the resulting token, tokenizer timelines, and remainder of the string

        :param string: The text string to tokenize
        :param trie: The `TokenTrie` object to use for tokenization
        :return: A tuple of the output `Token`, the remainder of ``string``, and a list of timelines
        """

        # Is this a byte literal?
        if string.startswith(r"\x") or string.startswith(r"\u"):
            length = 4 if string.startswith(r"\x") else 6
            string, remainder = string[:length], string[length:]
            token = IllegalToken(bytes.fromhex(string.lstrip(r"\ux")))

            return token, remainder, self.next(token, remainder)

        # Is this a var prefix?
        for leading_byte, prefix in TIToken.var_prefixes.items():
            if string.startswith(prefix):
                length = len(prefix) + 2
                string, remainder = string[:length], string[length:]
                token = IllegalToken(bytes([leading_byte, int(string[-2:], 16)]))

                return token, remainder, self.next(token, remainder)

        # Is there a token separator?
        if string.startswith(("␟", " ", "‌")):
            string = string[1:]

        # Is there a backslash?
        if string.startswith("\\"):
            tokens = trie.match(string[1:])
            token, remainder = tokens[0]

        else:
            tokens = trie.match(string)

            # Is this a glyph?
            if string[0] in punctuation and len(tokens) > 1:
                tokens.pop()

            token, remainder = tokens[self.mode]

        # Are we out of tokens?
        if self.length == self.max_length:
            return token, remainder, [[]]

        return token, remainder, self.next(token, remainder)

    def next(self, token: TIToken, remainder: str) -> list[list['TokenizerState']]:
        """
        Determines the next tokenizer timelines given a token

        The current state is popped from the stack, and the states returned by this method are pushed.

        1. The current state is popped from the stack.
        2. All possible timelines are determined, each a list of states.
        3. For each separate timeline, those states are added its stack.

        If a list of states in a timeline is...
            - empty, then the timeline is exiting the current state.
            - length one, then the timeline's current state is being replaced by a new state.
            - length two, then the timeline is entering a new state, able to exit back to this one.

        :param token: The current token
        :param remainder: The remaining string content to tokenize
        :return: A list of timelines (each a list of states)
        """

        return [[type(self)(self.mode, self.accept, self.length + 1)]]


class IllegalState(TokenizerState):
    """
    Tokenizer state which indicates its timeline must be pruned
    """


class MaxMode(TokenizerState):
    """
    Maximal munching mode
    """

    def __init__(self, mode: int = 0, accept: bool = True, length: int = 0):
        super().__init__(mode, accept, length)


class MinMode(TokenizerState):
    """
    Minimal munching mode
    """

    def __init__(self, mode: int = -1, accept: bool = True, length: int = 0):
        super().__init__(mode, accept, length)


class Line(TokenizerState):
    """
    State which is always exited after a line break or STO
    """

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        match token.bits:
                 # STO (→)  Line break
            case b'\x04' | b'\x3F':
                return [[]]

            case _:
                return super().next(token, remainder)


class Name(MinMode, Line):
    """
    Valid var identifiers
    """

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        #  Digits                              Uppercase letters (and theta)
        if b'\x30' <= token.bits <= b'\x39' or b'\x41' <= token.bits <= b'\x5B':
            return super().next(token, remainder)

        else:
            return [[]]


class ListName(Name):
    """
    List names
    """

    max_length = 5


class ProgramName(Name):
    """
    Program names
    """

    max_length = 8


class String(Line):
    """
    Strings
    """

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        match token.bits:
            case b'\x04':
                return [[StringTarget(self.mode, self.accept)]]

            case b'\x2A':
                return [[StringSto(self.mode, self.accept)]]

            case _:
                return super().next(token, remainder)


class StringStart(Line):
    """
    Opening quote of a string
    """

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        match token.bits:
            case b'\x2A':
                return [[String(self.mode, self.accept)]]

            case _:
                return [[]]


class StringSto(Line):
    """
    STO immediately following a string
    """

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        match token.bits:
            case b'\x04':
                return [[StringTarget(self.mode, self.accept)]]

            case _:
                return [[]] if self.accept else [[IllegalState(0)]]


class StringTarget(Line):
    """
    STO target of a string
    """

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        match self.mode, token.bits.startswith(b'\x5E'), self.accept:
            case (0, True, _) | (0, _, True) | (-1, False, _):
                return [[]]

            case _:
                return [[IllegalState(0)]]


class SmartMode(TokenizerState):
    """
    Smart tokenization mode
    """

    def __init__(self, mode: int = 0, accept: bool = True, length: int = 0):
        super().__init__(mode, accept, length)

    def next(self, token: TIToken, remainder: str) -> list[list[TokenizerState]]:
        match token.bits:
            #    "
            case b'\x2A':
                return [[self, String(0, False)], [self, String(-1)]]

            #    prgm
            case b'\x5F':
                return [[self, ProgramName()]]

            #    Send(     String>Equ(
            case b'\xE7' | b'\xBB\x56':
                return [[self, StringStart(0)]]

            #    |L
            case b'\xEB':
                return [[self, ListName()]]

            case _:
                return super().next(token, remainder)


__all__ = ["TokenizerState", "IllegalState", "MaxMode", "MinMode", "SmartMode",
           "Line", "Name", "ListName", "ProgramName",
           "String", "StringStart", "StringSto", "StringTarget"]
