from typing import Callable, Union, Any, Iterator, Generator, Tuple, TypeVar, Container
from enum import Enum
from copy import deepcopy
from .utils import consume
from itertools import islice
from functools import partial, reduce
"""
Option needs to mimic an Enum of one of two choices:
    Some(T) => basically not None
    None => None

It wraps these two with functionality to process the Option
while avoiding exposing the wrapped value. This suppresses
bare None errors, and promotes a functional style of programming


Option(val) => Some(val) or None

myopt = Option(val)
"""


class Option:
    def __init__(self, value):
        self.value = value


    def __eq__(self, other):
        return self.value == other.value


    def __str__(self):
        return f'Option.Some({self.value})'


    def unwrap(self):
        if not self.is_some():
            raise ValueError("Bare 'None' not allowed")

        return self.value


    def is_some(self):
        return self.value is not None


    def is_none(self):
        return self.value is None


    def contains(self, value):
        return self.value == value if self.is_some() else False


    def expect(self, message):
        if self.is_some():
            return self.value
        else:
            raise ValueError(message)


    def unwrap_or(self, default):
        return self.value if self.is_some() else default


    def unwrap_or_else(self, f: Callable):
        return self.value if self.is_some() else f()


    def map(self, f: Callable):
        """
        These all get evaluated greedily, might be worth making these
        lazy somehow. Generators?
        """
        return Option(f(self.value))


    def map_or(self, f: Callable, default):
        return Option(f(self.value) if self.is_some() else default)


    def map_or_else(self, f: Callable, default: Callable):
        return Option(f(self.value) if self.is_some() else default())


    def ok_or(self, e: Exception):
        return Result(self.value if self.is_some() else e)


    def ok_or_else(self, e: Callable):
        """
        Transforms Option<T> into Result<T> if Some otherwise
            calls e which returns Exception<U>

        Example:

        ```python
        my_option = Option(4)
        assert my_option.ok_or_else(lambda: Exception(5)).unwrap() == 4

        my_option = Option(None)
        assert my_option.ok_or_else(lambda: Exception(5)).is_err()
        ```
        """
        return Result(self.value if self.is_some() else e())


    def iter(self):
        if hasattr(self.value, '__iter__'):
            return Iter(iter(self.value))
        else:
            return Iter((val for val in (self.value,)))


    def and_(self, other):
        if self.is_some() and other.is_some():
            return other
        else:
            return Option(None)


    def and_then(self, f: Callable):
        if not self.is_some():
            return Option(None)
        else:
            return Option(f(self.value))


    def filter(self, predicate):
        if self.is_none():
            return Option(None)
        else:
            return Option(next(filter(predicate, (self.value,)), None))


    def or_(self, other):
        if self.is_some():
            return self
        else:
            return other


    def or_else(self, f: Callable):
        if self.is_some():
            return self
        else:
            return Option(f())


    def xor(self, other):
        tup = (self.is_some(), other.is_some())
        if True in tup and not all(tup):
            return next((opt for opt in (self, other) if opt.is_some()))
        else:
            return Option(None)


    def insert(self, value):
        self.value = value


    def get_or_insert(self, value):
        if self.is_none():
            self.value = value
            return value


    def get_or_insert_with(self, f: Callable):
        if self.is_none():
            self.value = f()
            return self.value


    def take(self):
        new_ = Option(self.value)
        self.value = None
        return new_


    def replace(self, value):
        new_ = Option(self.value)
        self.value = value
        return new_


    def zip(self, other):
        if self.is_none() or other.is_none():
            return Option(None)
        else:
            return Option((self.value, other.value))
