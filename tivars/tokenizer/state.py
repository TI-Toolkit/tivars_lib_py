"""
Encoder states
"""


from string import punctuation

from tivars.token import *
from tivars.trie import *


class TokenizerState:
    """
    Base class for tokenizer states

    Each state represents some encoding context which affects tokenization.
    """

    mode: int = 0
    """
    Whether to munch maximally (``0``) or minimally (``-1``)
    """

    max_length: int = None
    """
    The maximum number of tokens to emit before leaving this state
    """

    def __init__(self, length: int = 0):
        self.length = length

    def munch(self, string: str, trie: TITokenTrie) -> tuple[TIToken, str, list['TokenizerState']]:
        """
        Munch the input string and determine the resulting token, encoder state, and remainder of the string

        :param string: The text string to tokenize
        :param trie: The `TokenTrie` object to use for tokenization
        :return: A tuple of the output `Token`, the remainder of ``string``, and a list of states to add to the stack
        """

        # Is this a byte literal?
        if string.startswith(r"\x") or string.startswith(r"\u"):
            length = 4 if string.startswith(r"\x") else 6
            string, remainder = string[:length], string[length:]
            token = IllegalToken(bytes.fromhex(string.lstrip(r"\ux")))

            return token, remainder, self.next(token)

        # Is this a var prefix?
        for leading_byte, prefix in TIToken.var_prefixes.items():
            if string.startswith(prefix):
                length = len(prefix) + 2
                string, remainder = string[:length], string[length:]
                token = IllegalToken(bytes([leading_byte, int(string[-2:], 16)]))

                return token, remainder, self.next(token)

        # Is there a token separator?
        if string.startswith(("␟", " ", "‌")):
            string = string[1:]

        # Is there a backslash?
        if string.startswith("\\"):
            string = string[1:]
            self.mode = 0

        tokens = trie.match(string)
        if not tokens:
            raise ValueError("no tokenization options exist")

        # Is this a glyph?
        if string[0] in punctuation and len(tokens) > 1:
            tokens.pop()

        token, remainder = tokens[self.mode]

        # Are we out of tokens?
        if self.length == self.max_length:
            return token, remainder, []

        return token, remainder, self.next(token)

    def next(self, token: TIToken) -> list['TokenizerState']:
        """
        Determines the next tokenizer state given a token

        The current state is popped from the stack, and the states returned by this method are pushed.

        If the list of returned states is...
            - empty, then the tokenizer is exiting the current state.
            - length one, then the tokenizer's current state is being replaced by a new state.
            - length two, then the tokenizer is entering a new state, able to exit back to this one.

        :param token: The current token
        :return: A list of tokenizer states to add to the stack
        """

        return [type(self)(self.length + 1)]


class MaxMode(TokenizerState):
    """
    Maximal munching mode
    """

    mode = 0


class MinMode(TokenizerState):
    """
    Minimal munching mode
    """

    mode = -1


class Line(TokenizerState):
    """
    State which is always exited after a line break or STO
    """

    def next(self, token: TIToken) -> list[TokenizerState]:
        match token.bits:
            case b'\x04' | b'\x3F':
                return []

            case _:
                return super().next(token)


class Name(Line):
    """
    Valid var identifiers
    """

    mode = -1

    def next(self, token: TIToken) -> list[TokenizerState]:
        #  Digits                              Uppercase letters (and theta)
        if b'\x30' <= token.bits <= b'\x39' or b'\x41' <= token.bits <= b'\x5B':
            return super().next(token)

        else:
            return []


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

    mode = -1

    def next(self, token: TIToken) -> list[TokenizerState]:
        match token.bits:
            case b'\x2A':
                return []

            case _:
                return super().next(token)


class MaxString(String):
    """
    Maximally munched string
    """

    mode = 0


class MaxStart(Line):
    """
    State to initialize `MaxString`

    If any token besides ``"`` is encountered, this state is immediately exited to avoid cluttering the stack.
    """

    mode = 0

    def next(self, token: TIToken) -> list[TokenizerState]:
        match token.bits:
            case b'\x2A':
                return [MaxString()]

            case _:
                return []


class SmartMode(TokenizerState):
    """
    Smart tokenization mode
    """

    mode = 0

    def next(self, token: TIToken) -> list[TokenizerState]:
        match token.bits:
            #    "
            case b'\x2A':
                return [self, String()]

            #    prgm
            case b'\x5F':
                return [self, ProgramName()]

            #    Send(     String>Equ(
            case b'\xE7' | b'\xBB\x56':
                return [self, MaxStart()]

            #    |L
            case b'\xEB':
                return [self, ListName()]

            case _:
                return super().next(token)


__all__ = ["TokenizerState", "MaxMode", "MinMode", "SmartMode",
           "Line", "Name", "ListName", "ProgramName",
           "String", "MaxString", "MaxStart"]
