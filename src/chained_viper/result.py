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
        Maybe we want to transform a closure into a Result
        """
        try:
            val = f()
        except Exception as e:
            val = e
        finally:
            return Result(val)


    def map(self, key: Callable):
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
        if not self.is_ok():
            return Result(default(self.value))

        try:
            val = f(self.value)
        except Exception as e:
            val = type(e)(self.value)
        finally:
            return Result(val)


    def map_err(self, f: Callable):
        if not self.is_ok():
            return Result(f(self.value))
        else:
            return self


    def unwrap(self):
        if not self.is_ok():
            raise self.err_type(self.value)
        else:
            return self.value


    def is_ok(self):
        return not bool(self.err_type)


    def is_err(self):
        return bool(self.err_type)


    def ok(self):
        return Option(self.value) if self.is_ok() else Option(None)


    def err(self):
        return Option(self.value) if not self.is_ok() else Option(None)


    def iter_(self):
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
