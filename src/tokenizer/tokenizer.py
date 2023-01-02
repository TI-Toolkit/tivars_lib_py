from .parse import *


def tokenize(string: str, tokens: TokenMap) -> bytearray:
    data = bytearray(b'\0\0')
    max_length = min(len(string), max(map(len, tokens.keys())))
    within_string = False

    index = 0
    while index < len(string):
        if within_string:
            length = 1
            direction = 1
        else:
            length = max_length
            direction = -1

        while length <= max_length if within_string else length > 0:
            substring = string[index:][:length]
            if substring in tokens:
                value = tokens[substring].bytes
                data.extend(value)

                if substring == '"':
                    within_string = not within_string
                elif tokens[substring].terminator:
                    within_string = False

                index += length - 1
                break

            length += direction

        index += 1

    data_length = len(data) - 2
    data[0:2] = data_length.to_bytes(2, 'little')
    return data


__all__ = ["tokenize"]
