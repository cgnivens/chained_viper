from typing import Callable, Union, Any, Iterator, Generator, Tuple, TypeVar, Container
from enum import Enum
from copy import deepcopy
import sys
from .utils import consume
from itertools import islice
from functools import partial, reduce


class Result:
    """
    Result is either Ok or Err
    """
    def __init__(self, value):
        if isinstance(value, Exception):
            self.value = value.args[0]
            self.err_type = type(value)
        else:
            self.value = value
            self.err_type = None


    def __str__(self):
        type_ = "Ok" if self.is_ok() else "Err"
        return f"Result.{type_}({self.value})"



    def __eq__(self, other):
        return (self.value == other.value
            and self.err_type is other.err_type)


    @classmethod
    def into(cls, f: Callable):
        """
        Transform a function call/closure into a Result[T]. Calls
        the function
        """
        try:
            val = f()
        except Exception as e:
            val = e
        finally:
            return Result(val)


    def map(self, key: Callable):
        """
        Applies a function f[T] -> U to the value of an Ok Result[T].
        Returns another Result[U]. Doesn't do anything if Result
        is Err[T]


            r = Result.into(lambda: 1)
            assert r.map(lambda x: str(x)) == Result("1")

            r = Result.into(lambda: Exception(1))
            assert r.map(lambda x: str(x)) == Result(Exception(1))

        """
        if not self.is_ok():
            return Result(self.err_type(self.value))

        # gross! still working this out
        try:
            val = key(self.value)
        except Exception as e:
            val = type(e)(self.value)
        finally:
            return Result(val)


    def map_or(self, f: Callable, default: Any):
        """
        Apply a function f[T] to an Ok[T] which returns
        Result[U]. If Result is Err[T], return a default value
        Result[U]

            r = Result(1)
            assert r.map_or(lambda x: x + 1, 42) == Result(2)

            r = Result.into(lambda: Exception(1))
            assert r.map_or(lambda x: x + 1, 42) == Result(42)
        """
        if not self.is_ok():
            return Result(default)

        try:
            val = f(self.value)
        except Exception as e:
            val = type(e)(self.value)
        finally:
            return Result(val)


    # TODO: I think this should actually unwrap
    # and return a non-Result. Not sure about this one though
    def map_or_else(self, f: Callable, default: Callable):
        """
        Applies f[T] to Ok[T] and default[e] to Err[e]. Unwraps
        the values and allows for error handling:

            k = 21
            r = Result(1)
            assert r.map_or_else(lambda x: x + 1, lambda e: k * 2) == 2

            e = Result(Exception(1))
            assert e.map_or_else(lambda x: x + 1, lambda e: k * 2) == 42
        """
        if not self.is_ok():
            return default(self.value)

        try:
            val = f(self.value)
        except Exception as e:
            raise

        return val


    def map_err(self, f: Callable):
        """
        Applies f[T] to an Err[T] returning Err[U], otherwise does nothing
        and returns self

            r = Result(1)
            assert r.map_err(lambda x: x + 1) == Result(1)

            e = Result(Exception(1))
            assert e.map_err(lambda x: x + 1)
        """
        if not self.is_ok():
            return Result(self.err_type(
                f(self.value))
            )
        else:
            return self


    def unwrap(self):
        """
        Unwraps a Result[Ok[T], Err[e]]. Will raise a contained
        error and return T from Ok[T]

            r = Result(2)
            assert r.unwrap() == 2

            e = Result(Exception(2))
            try:
                assert e.unwrap() == 2
            except Exception as e:
                print(e)
        """
        if not self.is_ok():
            raise self.err_type(self.value)
        else:
            return self.value


    def is_ok(self):
        """
        Returns True if Result is an Ok, otherwise
        returns False if Exception type is wrapped

            assert Result(22).is_ok()
            assert not Result(Exception(22)).is_ok()
        """
        return not bool(self.err_type)


    def is_err(self):
        """
        Returns True if Result wraps an Exception type, otherwise
        returns False

            assert not Result(22).is_err()
            assert Result(Exception(22)).is_err()
        """
        return bool(self.err_type)


    def ok(self):
        """
        Converts an Ok[T] to Option[T] if Result is ok, else
        returns an Option[None]
        """
        return Option(self.value) if self.is_ok() else Option(None)


    def err(self):
        """
        Converts an Err[T] to Option[T] if Result is err, else
        return an Option[None]
        """
        return Option(self.value) if not self.is_ok() else Option(None)


    def iter_(self):
        """
        Iterates over the contents of an Ok[T] if supported, otherwise
        creates an iterator over a single element tuple of Ok[T]. If
        Result is an Err[e], returns an empty iterator

            r = Result(1)
            assert r.iter_().next() == Option(1)

            e = Result(Exception(1))
            assert r.iter_().next() == Option(None)

            r = Result('abc')
            assert r.iter_().next() == Option('a')

        This is the method recommended for chaining lazy
        operations on a Result, as the iterator will not evaluate them
        until something is done with it.
        """
        if not self.is_ok():
            return Iter([])
        else:
            try:
                return Iter(iter(self.value))
            except:
                return Iter((self.value,))


    def and_(self, other):
        if not self.is_ok():
            return self
        elif not other.is_ok():
            return other
        else:
            return other


    def and_then(self, f: Callable):
        if not self.is_ok():
            return self

        try:
            val = f(self.value)
        except Exception as e:
            val = type(e)(self.value)
        finally:
            return Result(val)


    def or_(self, other):
        if self.is_ok():
            return self
        elif other.is_ok():
            return other
        else:
            return other


    def or_else(self, f: Callable):
        if self.is_ok():
            return self

        try:
            val = f(self.value)
        except Exception as e:
            val = type(e)(self.value)
        finally:
            return Result(val)


    def unwrap_or(self, default):
        if not self.is_ok():
            return default
        else:
            return self.value


    def unwrap_or_else(self, f: Callable):
        if not self.is_ok():
            return f(self.value)
        else:
            return self.value


    def expect(self, message):
        if not self.is_ok():
            raise self.err_type(message)
        else:
            return self.value


    def expect_err(self, message):
        if self.is_ok():
            raise Exception(message)
        else:
            return self.value


    def unwrap_err(self):
        if not self.is_ok():
            return self.value
        else:
            raise Exception(self.value)
