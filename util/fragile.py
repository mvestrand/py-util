__all__ = ["fragile"]

import typing as t

class fragile(object):
    """Enclose an object in a with statement to make it breakable
        >>> with fragile(open(path)) as f:
        >>>     if condition:
        >>>         raise fragile.Break
        Taken from "https://stackoverflow.com/questions/11195140/break-or-exit-out-of-with-statement"
    """
    class Break(Exception):
      """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error
