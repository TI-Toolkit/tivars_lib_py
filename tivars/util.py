"""
Common utilies (mostly of the string variety)
"""


import re

from .flags import Flags


def hex_format(data: bytes, format_spec: str) -> str:
    """
    Helper function for formatting hex data

    The format specifier takes the form ``{width}?{case}{sep}?``.
    - ``width`` is the width of groups of hex digits; negative values group from the end (defaults to no groups)
    - ``case`` is `x` or `X` to dictate the case of the hex digits
    - ``sep`` is a single character to separate groups of hex digits (defaults to none)

    :param data: The data to format
    :param format_spec: The f-string specifier to format the hexdump
    :return: ``data`` formatted in hex with some width, case, and separator
    """

    if match := re.fullmatch(r"(?P<width>[+-]?\d+)?(?P<case>[xX])(?P<sep>\D)?", format_spec):
        match match["sep"], match["width"]:
            case None, None:
                string = data.hex()

            case sep, None:
                string = data.hex(sep)

            case None, width:
                string = data.hex(" ", int(width))

            case sep, width:
                string = data.hex(sep, int(width))

        return string.lower() if match["case"] == "x" else string.upper()

    raise TypeError(f"unsupported format string passed to hex formatter")


def mode_format(flags: Flags, *options: str) -> str:
    """
    Format a `Flags` field akin to an on-calc mode selection

    :param flags: The `Flags` field to format
    :param options: The names of the mode options to show
    :return: The contents of ``flags`` formatted as a mode selection
    """

    return " | ".join(f"[{option}]" if getattr(type(flags), option) in flags else option for option in options)


def replacer(string: str, replacements: dict[str, str]) -> str:
    """
    Iteratively applies string replacements

    :param string: The input string
    :param replacements: The replacements to make
    :return: ``string`` with all replacements made in-order
    """

    for substring, replacement in replacements.items():
        string = string.replace(substring, replacement)

    return string


def squash(string: str) -> str:
    """
    Removes all spaces from a string

    :param string: The input string
    :return: ``string`` with all spaces removed
    """

    return ''.join(string.split())


def trim_list(lst: list, length: int, joiner: str = "\n") -> str:
    """
    Trim a list to some length (from the right), then join it, indicating if any trimming occurred by an ellipsis

    :param lst: The list to trim
    :param length: The length to trim ``lst`` to
    :param joiner: The string to join ``lst` by (defaults to a newline)
    :return: ``lst`` trimmed to ``length`` and joined by ``joiner``
    """

    if len(lst) <= length:
        return joiner.join(map(str, lst))

    else:
        return joiner.join([*map(str, lst[:length]), "..."])


def trim_string(string: str, length: int) -> str:
    """
    Trim a string (from the right) to some length, indicating if any trimming occurred by an ellipsis

    :param string: The string to trim
    :param length: The length to trim ``string`` to
    :return: ``string`` trimmed to ``length``
    """

    if len(string) <= length:
        return string

    else:
        return string[:length] + "..."


__all__ = ["hex_format", "mode_format", "replacer", "squash", "trim_list", "trim_string"]
