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
    """
    Python version of Rust's Option. Wraps any type and disallows
    unwrapped Nones. Allows for chained operations and lazy evaluation.
    Lazy evaluation is done through the Option.iter() method, otherwise
    all operations are greedily evaluated.
    """
    def __init__(self, value):
        self.value = value


    def __eq__(self, other):
        return self.value == other.value


    def __str__(self):
        return f'Option.Some({self.value})' if self.is_some() else 'Option.None'


    def unwrap(self):
        """
        Attempts to unwrap the Option into its contained
        value. Unwrapping a None will raise a ValueError
        """
        if not self.is_some():
            raise ValueError("Bare 'None' not allowed")

        return self.value


    def is_some(self):
        """
        Checks if the Option is not wrapping None

            opt = Option(5)
            opt.is_some()
            True

            opt = Option(None)
            opt.is_some()
            False
        """
        return self.value is not None


    def is_none(self):
        """
        Checks if the Option is wrapping None

            opt = Option(5)
            opt.is_none()
            False

            opt = Option(None)
            opt.is_none()
            True
        """
        return self.value is None


    def contains(self, value):
        """
        Checks to see if the Option contains an explicit value.
        Similar to equivalence checking against another Option

            opt = Option(5)
            opt.contains(5)
            True
        """
        return self.value == value if self.is_some() else False


    def expect(self, message):
        """
        Expects a non-null Option and returns the value. Will
        raise an Exception with the chosen method otherwise.
        Similar to unwrap except you specify the error message

            opt = Option(5).expect("Error!")
            opt == 5
            True

            opt = Option(None).expect("Error!")
            Exception:
                Error!
        """
        if self.is_some():
            return self.value
        else:
            raise Exception(message)


    def unwrap_or(self, default):
        """
        Unwraps an Option if it is_some(), otherwise return
        a default value. Helpful for avoiding ValueErrors on
        unwrapping a None value

            opt = Option(5)
            opt.unwrap_or(42) == 5
            True

            opt = Option(None)
            opt.unwrap_or(42) == 42
            True

            # Better than this approach
            try:
                val = opt.unwrap()
            except:
                val = 42

        """
        return self.value if self.is_some() else default


    def unwrap_or_else(self, f: Callable):
        """
        Allows for a closure to be passed to handle Nones instead
        of just unwrapping them.

            opt = Option(5)
            opt.unwrap_or_else(lambda: 42) == 5
            True

            opt = Option(None)
            opt.unwrap_or_else(lambda: 42) == 42
            True

            # Better than this approach
            try:
                val = opt.unwrap()
            except:
                val = f()

        Note that the closure does not use arguments. If you need your closure
        to take args, use partial function application:

            from functools import partial

            def some_func(a):
                return a + 1

            f = partial(some_func, a=22)

            Option(None).unwrap_or_else(f) == 23
            True
        """
        return self.value if self.is_some() else f()


    def map(self, f: Callable):
        """
        Applies a closure/function to the value wrapped in the Option
        if it is not a None, otherwise returns the Option(None).

            opt = Option(5)
            opt.map(lambda x: x + 1) == Option(6)
            True

            opt = Option(None)
            opt.map(lambda x: x + 1) == Option(None)
            True

        These are evaluated greedily. For a more lazy evaluation style,
        use the Option.iter() method to transform it into an iterator:

            opt = Option(5).iter()
            opt = opt.map(lambda x: x + 1) # hasn't evaluated yet
            opt.next() == Option(6) # evaluates here
        """
        return Option(f(self.value)) if self.is_some() else self


    def map_or(self, f: Callable, default):
        """
        Applies a function to the value of an Option provided it is
        not a None, otherwise returns a default value

            opt = Option(5)
            opt.map_or(lambda x: x + 1, 42) == Option(6)
            True

            opt = Option(None)
            opt.map_or(lambda x: x + 1, 42) == Option(42)
            True

        The function is greedily evaluated
        """
        return Option(f(self.value) if self.is_some() else default)


    def map_or_else(self, f: Callable, default: Callable):
        """
        Applies a function to the value of an Option provided it is
        not a None, otherwise calls a default function

            opt = Option(5)
            opt.map_or(lambda x: x + 1, lambda: 42) == Option(6)
            True

            opt = Option(None)
            opt.map_or(lambda x: x + 1, lambda: 42) == Option(42)
            True

        The function and default are greedily evaluated
        """
        return Option(f(self.value) if self.is_some() else default())


    def ok_or(self, e: Exception):
        """
        Converts an Option<T> into a Result<T>, and a
        None into an Err<T>

            opt = Option(5)
            opt.ok_or(Exception("Bad Value")) == Result(5)
            True

            opt = Option(None)
            opt.ok_or(Exception("Bad Value")) == Result(Exception("Bad Value"))
            True
        """
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
        """
        Transforms an Option into an Iterator over its contained
        value. If the contained value doesn't support iteration, then
        a single-element iterator is created

            my_iter = Option(5).iter()
            my_iter.next() == Option(5)
            True

            # int isn't iterable, so single-element
            # iterator is exhausted
            my_iter.next() == Option(None)

            # Iterates over each element in the string
            my_iter = Option("hello").iter()
            my_iter.next() == Option("h")
            True

        Useful for lazily applying a function to a value in an Option.
        If you want a single-element iterator of iterable types, wrap
        into a single-element tuple:

            my_iter = Option(('hello',)).iter()
            my_iter.next() == Option("hello")
            True

            # Iterator is now empty
            my_iter.next().is_none()
            True
        """
        if hasattr(self.value, '__iter__'):
            return Iter(iter(self.value))
        else:
            return Iter((val for val in (self.value,)))


    def and_(self, other):
        """
        Returns other if both self and other are Some, otherwise
        returns Option(None). Useful for control flow:

            opt1, opt2, opt3 = Option(1), Option(2), Option(None)

            opt1.and_(opt2).is_some()
            True

            opt1.and_(opt3).is_none()
            True

            opt3.and_(opt1).is_none()
            True
        """
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
