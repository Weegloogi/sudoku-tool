from typing import Iterable, Callable, Any


def any(it: Iterable, key: Callable[[Any], bool] = None) -> bool:
    """
    Similar to the built-in `any` function, but with an optional argument `key` that allows for customs measurement keys
    :param it: iterable to scan
    :param key: optional key
    :return: true if the key returns true on any of the iterable elements
    """
    if not key:
        key = bool

    for i in it:
        if key(i):
            return True
    return False


def all(it: Iterable, key: Callable[[Any], bool] = None) -> bool:
    """
    Similar to the built-in `all` function, but with an optional argument `key` that allows for customs measurement keys
    :param it: iterable to scan
    :param key: optional key
    :return: true if the key returns true on any of the iterable elements
    """
    if not key:
        key = bool

    for i in it:
        if not key(i):
            return False
    return True


def filter(it: Iterable, key: Callable[[Any], bool] = None) -> list:
    """
    filters an iterable object using key
    :param it: the iterable to filter
    :param key: optional key
    :return: the list of filtered elements
    """

    if not key:
        key = bool

    res = []
    for i in it:
        if key(i):
            res.append(i)

    return res