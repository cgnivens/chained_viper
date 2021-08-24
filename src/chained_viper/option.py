from typing import Callable, Union, Any, Iterator, Generator, Tuple, TypeVar, Container
from enum import Enum
from copy import deepcopy
from .utils import consume
from itertools import islice
from functools import partial, reduce
"""
Option needs to mimic an Enum of one of two choices:
    Some(T) => T is not None
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
        """Tests equality between two Options

        Parameters
        ----------
        other: Option
            Another option to compare against

        Returns
        -------
        bool
        """
        return self.value == other.value


    def __str__(self):
        return f'Option.Some({self.value})' if self.is_some() else 'Option.None'


    def unwrap(self):
        """Attempts to unwrap the Option into its contained
        value. Unwrapping a None will raise a ValueError

        Returns
        -------
        value: Any
            Returns the wrapped value so long as it isn't None

        Raises
        ------
        ValueError
            Only if unwrapping a None value


        Examples
        --------
        Unwrapping a non-None Option returns the value:

        >>> opt = Option(5)
        >>> assert opt.unwrap() == 5


        Unwrapping a None raises a ValueError
        >>> opt = Option(None)
        >>> try:
        ...     val = opt.unwrap()
        ... except ValueError:
        ...     print("Error caught")
        ...
        Error caught
        """
        if not self.is_some():
            raise ValueError("Bare 'None' not allowed")

        return self.value


    def is_some(self):
        """Checks if the Option is not wrapping None

        Returns
        -------
        bool

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.is_some()

        >>> opt = Option(None)
        >>> assert not opt.is_some()
        """
        return self.value is not None


    def is_none(self):
        """
        Checks if the Option is wrapping None

        Returns
        -------
        bool

        Examples
        --------
        >>> opt = Option(5)
        >>> assert not opt.is_none()

        >>> opt = Option(None)
        >>> assert opt.is_none()
        """
        return self.value is None


    def contains(self, value):
        """
        Checks to see if the Option contains an explicit value.
        Similar to equivalence checking against another Option

        Parameters
        ----------
        value: Any

        Returns
        -------
        bool

        Examples
        --------
        >>> opt = Option(5)
        >>> assert opt.contains(5)
        """
        return self.value == value if self.is_some() else False


    def expect(self, message):
        """
        Expects a non-null Option and returns the value. Will
        raise an Exception with the chosen method otherwise.
        Similar to unwrap except you specify the error message

        Parameters
        ----------
        message: str
            The message to be displayed in the event that self
            is a None

        Raises
        ------
        Exception

        Returns
        -------
        self.value

        Examples
        --------
        >>> opt = Option(5).expect("Error!")
        >>> assert opt == 5

        >>> opt = Option(None).expect("Error!")
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

        Parameters
        ----------
        default: Any
            Any value to be returned if self.is_none()

        Returns
        -------
        self.value or default

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.unwrap_or(42) == 5

        >>> opt = Option(None)
        >>> assert opt.unwrap_or(42) == 42

        # Better than this approach
        >>> try:
        ...     val = opt.unwrap()
        ... except:
        ...     val = 42
        ...
        >>> assert val == 42

        """
        return self.value if self.is_some() else default


    def unwrap_or_else(self, f: Callable):
        """
        Allows for a closure to be passed to handle Nones instead
        of just unwrapping them.

        Parameters
        ----------
        f: Callable
            Any function that takes no arguments

        Returns
        -------
        self.value or the output of f()

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.unwrap_or_else(lambda: 42) == 5

        >>> opt = Option(None)
        >>> assert opt.unwrap_or_else(lambda: 42) == 42

        # Replaces this approach
        >>> try:
        ...     val = opt.unwrap()
        ... except:
        ...     val = f()
        ...
        >>> assert val == 42

        Note that the closure does not use arguments. If you need your closure
        to take args, use partial function application:

        >>> from functools import partial

        >>> def some_func(a):
        ...     return a + 1

        >>> f = partial(some_func, a=22)

        >>> assert Option(None).unwrap_or_else(f) == 23
        """
        return self.value if self.is_some() else f()


    def map(self, f: Callable):
        """
        Applies a closure/function to the value wrapped in the Option
        if it is not a None, otherwise returns the Option(None).

        Parameters
        ----------
        f: Callable
            Single argument function to be applied to self.value

        Returns
        -------
        Option(U) where f(T) -> U if T is not None

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.map(lambda x: x + 1) == Option(6)

        >>> opt = Option(None)
        >>> assert opt.map(lambda x: x + 1) == Option(None)

        These are evaluated greedily. For a more lazy evaluation style,
        use the Option.iter() method to transform it into an iterator:

        >>> opt = Option(5).iter()
        >>> opt = opt.map(lambda x: x + 1) # hasn't evaluated yet
        >>> opt.next() == Option(6) # evaluates here
        """
        return Option(f(self.value)) if self.is_some() else self


    def map_or(self, f: Callable, default):
        """
        Applies a function to the value of an Option provided it is
        not a None, otherwise returns a default value

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.map_or(lambda x: x + 1, 42) == Option(6)

        >>> opt = Option(None)
        >>> assert opt.map_or(lambda x: x + 1, 42) == Option(42)

        The function is greedily evaluated
        """
        return Option(f(self.value) if self.is_some() else default)


    def map_or_else(self, f: Callable, default: Callable):
        """
        Applies a function to the value of an Option provided it is
        not a None, otherwise calls a default function

        Examples
        --------
        >>> opt = Option(5)
        >>> assert opt.map_or(lambda x: x + 1, lambda: 42) == Option(6)

        >>> opt = Option(None)
        >>> assert opt.map_or(lambda x: x + 1, lambda: 42) == Option(42)

        The function and default are greedily evaluated
        """
        return Option(f(self.value) if self.is_some() else default())


    def ok_or(self, e: Exception):
        """
        Converts an Option<T> into a Result<T>, and a
        None into an Err<T>

        Examples
        --------
        >>> opt = Option(5)
        >>> assert opt.ok_or(Exception("Bad Value")) == Result(5)

        >>> opt = Option(None)
        >>> assert opt.ok_or(Exception("Bad Value")).is_err()
        """
        return Result(self.value if self.is_some() else e)


    def ok_or_else(self, e: Callable):
        """
        Transforms Option<T> into Result<T> if Some otherwise
            calls e which returns Exception<U>

        Examples
        --------

        >>> my_option = Option(4)
        >>> assert my_option.ok_or_else(lambda: Exception(5)).unwrap() == 4

        >>> my_option = Option(None)
        >>> assert my_option.ok_or_else(lambda: Exception(5)).is_err()
        """
        return Result(self.value if self.is_some() else e())


    def iter(self):
        """
        Transforms an Option into an Iterator over its contained
        value. If the contained value doesn't support iteration, then
        a single-element iterator is created

        Examples
        --------
        >>> my_iter = Option(5).iter()
        >>> assert my_iter.next() == Option(5)

        >>> # int isn't iterable, so single-element
        >>> # iterator is exhausted
        >>> assert my_iter.next() == Option(None)

        >>> # Iterates over each element in the string
        >>> my_iter = Option("hello").iter()
        >>> assert my_iter.next() == Option("h")

        Useful for lazily applying a function to a value in an Option.
        If you want a single-element iterator of iterable types, wrap
        into a single-element tuple:

        >>> my_iter = Option(('hello',)).iter()
        >>> assert my_iter.next() == Option("hello")

        >>> # Iterator is now empty
        >>> assert my_iter.next().is_none()
        """
        if hasattr(self.value, '__iter__'):
            return Iter(iter(self.value))
        else:
            return Iter((val for val in (self.value,)))


    def and_(self, other):
        """
        Returns other if both self and other are Some, otherwise
        returns Option(None). Useful for control flow

        Examples
        --------
        >>> opt1, opt2, opt3 = Option(1), Option(2), Option(None)

        >>> assert opt1.and_(opt2).is_some()

        >>> assert opt1.and_(opt3).is_none()

        >>> assert opt3.and_(opt1).is_none()
        """
        if self.is_some() and other.is_some():
            return other
        else:
            return Option(None)


    def and_then(self, f: Callable):
        """
        Applies a function to the value of a non-null Option, otherwise
        returns Option(None)

        Examples
        --------
        >>> opt = Option(5)
        >>> assert opt.and_then(lambda x: x+1) == Option(6)

        >>> opt = Option(None)
        >>> assert opt.and_then(lambda x: x+1).is_none()
        """
        if not self.is_some():
            return Option(None)
        else:
            return Option(f(self.value))


    def filter(self, predicate: Union[Callable, None]):
        """
        Returns Option(None) if self is None. Otherwise calls
        the predicate on an iterator of one element, self.value

        Parameters
        ----------
        predicate: Union[Callable, None]
            Either a function that will return a boolean
            or None which will default to the bool() function

        Returns
        -------
        Option[T]
            T is either None or the contained value if predicate
            evaluates to True

        Examples
        --------
        >>> opt = Option(5)
        >>> assert opt.filter(lambda x: not x % 2).is_none()
        >>> assert opt.filter(lambda x: x % 2).is_some()

        >>> assert Option(None).filter(bool).is_none()
        """
        if self.is_none():
            return Option(None)
        else:
            return Option(next(filter(predicate, (self.value,)), None))


    def or_(self, other):
        """
        Returns self if self is not a None, otherwise returns other

        Parameters
        ----------
        other: Option[U]

        Returns
        -------
        Option[T]
            Where T is either the first non-null wrapped value
            or None

        Examples
        --------

        >>> opt1, opt2, opt3 = Option(1), Option(2), Option(None)

        >>> assert opt1.or_(opt2) == Option(1)
        >>> assert opt1.or_(opt3) == Option(1)

        >>> assert opt3.or_(opt2) == Option(2)
        >>> assert opt3.or_(opt3) == Option(None)
        """
        if self.is_some():
            return self
        else:
            return other


    def or_else(self, f: Callable):
        """
        Returns self if self is Some, otherwise calls a function

        Parameters
        ----------
        f: Callable

        Returns
        -------
        Option[T]
            T is either self.value if self.is_some() or the result
            of f()

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.or_else(lambda: 42) == Option(5)
        >>> assert Option(None).or_else(lambda: 42) == Option(42)
        """
        if self.is_some():
            return self
        else:
            return Option(f())


    def xor(self, other):
        """
        Exclusive or for two Option types. Returns the first Some provided
        both are not Some, otherwise returns None

        Parameters
        ----------
        other: Option[T]

        Returns
        -------
        Option[T]

        Examples
        --------

        >>> opt1, opt2, opt3 = (Option(val) for val in [1, 2, None])

        >>> assert opt1.xor(opt2).is_none()
        >>> assert opt1.xor(opt3) == Option(1)
        >>> assert opt3.xor(opt2) == Option(2)
        """
        tup = (self.is_some(), other.is_some())
        if True in tup and not all(tup):
            return next((opt for opt in (self, other) if opt.is_some()))
        else:
            return Option(None)


    def insert(self, value):
        """
        This is functionally identical to setting the value attribute
        manually

        Parameters
        ----------
        value: Any

        Examples
        --------
        >>> # These two code snippets are functionally identical
        >>> opt = Option(2)
        >>> opt.value = 3

        >>> opt2 = Option(5)
        >>> opt2.insert(3)

        >>> assert opt == opt2
        """
        self.value = value


    def take(self):
        """
        Strips the value from self and returns a new Option, changing
        self to a None

        Returns
        -------
        Option[T]

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.take() == Option(5)

        >>> # original option is now None
        >>> assert opt.is_none()
        """
        new_ = Option(self.value)
        self.value = None
        return new_


    def replace(self, value):
        """
        Replaces self.value with a new value, returning
        an Option of the original value

        Parameters
        ----------
        value: Any

        Returns
        -------
        Option[T]
            Where T is the original value wrapped by self

        Examples
        --------

        >>> opt = Option(5)
        >>> assert opt.replace(6) == Option(5)

        >>> assert opt == Option(6)
        """
        new_ = Option(self.value)
        self.value = value
        return new_


    def zip(self, other):
        """
        Create an Option of a tuple of the two contained values, provided
        self and other are not None. Otherwise returns Option(None)

        Parameters
        ----------
        other: Option[U]

        Returns
        -------
        Option[(T, U)]

        Examples
        --------

        >>> opt1, opt2, opt3 = Option(1), Option(2), Option(None)

        >>> assert opt1.zip(opt2) == Option((1, 2))
        >>> assert opt1.zip(opt3).is_none()
        """
        if self.is_none() or other.is_none():
            return Option(None)
        else:
            return Option((self.value, other.value))
