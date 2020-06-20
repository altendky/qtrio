"""This module provides general Python related utilities that are not Qt nor Trio
specific.
"""


def identifier_path(it):
    """Generate an identifier based on an object's module and qualified name.  This can
    be useful such as for adding attributes to existing objects while minimizing odds
    of collisions and maximizing traceability of the related party.

    Args:
        it: The object to generate the identifer from.
    """
    return "__" + "_".join(it.__module__.split(".") + [it.__qualname__])
