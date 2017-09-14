__author__ = 'lehmann'

import time


def timeit(method):
    """
    Decorator for measuring execution time of a function.
    Usage:

        >>> @timeit
        ... def f1():
        ...     time.sleep(1)
        ...     print 'f1'
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te - ts))
        return result

    return timed


def string_remove_by_index(string, start_index, length):
    s1 = string[:start_index]
    s2 = string[start_index + length:]
    return s1 + s2


def string_insert(s1, s2, index):
    return s1[:index] + s2 + s1[index:]


def string_to_float(s):
    try:
        return float(s.replace(',', '.'))
    except ValueError:
        return 0.0
