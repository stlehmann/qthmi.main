"""Utilities for qthmi.main.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-06-11 18:16:58
:last modified by:   Stefan Lehmann
:last modified time: 2018-07-09 16:39:43

"""


from typing import Any, Callable
import time


def timeit(method: Callable) -> Callable:
    """Measure execution time of a function.

    **Decorator.**

    Usage:

        >>> @timeit
        ... def f1():
        ...     time.sleep(1)
        ...     print 'f1'
    """
    def timed(*args: Any, **kw: Any) -> Any:
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te - ts))
        return result

    return timed


def string_remove_by_index(string: str, start_index: int, length: int) -> str:
    """Remove substring of length, start at start_index."""
    s1 = string[:start_index]
    s2 = string[start_index + length:]
    return s1 + s2


def string_insert(s1: str, s2: str, index: int) -> str:
    """Insert string s2 in s1 at index."""
    return s1[:index] + s2 + s1[index:]


def string_to_float(s: str) -> float:
    """Convert string to float."""
    try:
        return float(s.replace(',', '.'))
    except ValueError:
        return 0.0
