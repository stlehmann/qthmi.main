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

        print ('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts))
        return result

    return timed
