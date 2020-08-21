"""This module provides general Python related utilities that are not Qt nor Trio
specific.
"""
import typing


# TODO: could support some more things
#       https://docs.python.org/3/library/stdtypes.html#definition.__qualname__
def identifier_path(it: typing.Union[typing.Type[object], typing.Callable]) -> str:
    """Generate an identifier based on an object's module and qualified name.  This can
    be useful such as for adding attributes to existing objects while minimizing odds
    of collisions and maximizing traceability of the related party.

    Args:
        it: The object to generate the identifer from.

    Returns:
        The generated identifier string.
    """
    return "__" + "_".join(it.__module__.split(".") + [it.__qualname__])
