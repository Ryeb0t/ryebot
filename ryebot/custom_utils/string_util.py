def str_to_list(string: str, delim: str=',', trim: bool=True):
    """Convert a string to a list.

    Return an empty list if the string is `None`.

    Parameters
    ----------
    1. string : str
        - The input string to convert.
    2. delim : str
        - The delimiter between list items in the input string.
    3. trim : bool
        - Whether to trim list items.
    """

    if not string:
        return []
    result_list = list(string.split(delim))
    if trim:
        result_list = [str.strip() for str in result_list]
    return result_list


def csharp_string_concat(*args):
    """A Python version of C#'s `String.Concat()`.

    Similar to `join()`, but join the parameters instead of an iterable.
    """

    return ''.join(args)


def lstrip_max(string: str, characters: str=' ', max_chars: int=1):
    """Return a copy of the string with leading whitespace removed.

    Similar to `lstrip()`, but do not strip more than `max_chars` characters.
    """

    chars = list(characters)

    for _ in range(max_chars):
        if string[0] in chars:
            string = string[1:]
        else:
            break

    return string


def lcfirst(string: str):
    """Return the string with the first character in lower case."""
    return _change_first_case(string, upper=False)

def ucfirst(string: str):
    """Return the string with the first character in upper case."""
    return _change_first_case(string, upper=True)


def _change_first_case(string: str, upper: bool):

    if len(string) == 0:
        return ''

    if len(string) == 1:
        return string.upper() if upper else string.lower()

    return (string[0].upper() if upper else string[0].lower()) + string[1:]
