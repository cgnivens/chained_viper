
from typing import Callable, Union, Any, Iterator, Generator, Tuple, TypeVar, Container
from enum import Enum
from copy import deepcopy
from .utils import consume
from itertools import islice
from functools import partial, reduce


T = TypeVar('T')


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


    def map(self, key):
        if not self.is_ok():
            return Result(self.value)

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


    def map_or_else(self, f, default: Callable):
        if not self.is_ok():
            yield Result(default(self.value))

        try:
            val = f(self.value)
        except Exception as e:
            val = type(e)(self.value)
        finally:
            yield Result(val)


    def map_err(self, f: Callable):
        if not self.is_ok():
            return Result(f(self.value))
        else:
            return Result(self.value)


    def unwrap(self):
        if not self.is_ok():
            raise self.err_type(self.value)
        else:
            return self.value


    def is_ok(self):
        return bool(self.err_type)


    def is_err(self):
        return not bool(self.err_type)


    def ok(self):
        return Option(self.value) if self.is_ok() else Option(None)


    def err(self):
        return Option(self.value) if not self.is_ok() else Option(None)


    def iter_(self):
        if not self.is_ok():
            yield
        else:
            yield from Iter(iter(self.value))


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
        # print(f"self: {self} other: {other}")
        # print(self)
        # print(self.value)
        # print(other)
        # print(other.value)
        return self.value == other.value


    def __str__(self):
        return f'Option.Some({self.value})'


    def __iter__(self):
        return iter(self.value) if hasattr(self.value, '__iter__') else iter(self.value, )


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
        return Option(f(self.value)) if self.is_some() else default


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
            return Option(next(filter(predicate, (self.value,))))


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


Iter = TypeVar('Iter', Iterator, Generator)


class Iter:
    def __init__(self, iterator):
        if isinstance(iterator, Iter):
            self.iter_ = (item.value for item in iterator)
        else:
            self.iter_ = iterator if isinstance(iterator, Iterator) else iter(iterator)


    def __next__(self) -> Option:
        """
        Can't use self.next() here. I want this to be able to
        still raise StopIteration, but I shouldn't have to declare
        the default return type on
            empty_iterator.next()

        because IMO it should return Option<None>
        """
        return Option(next(self.iter_))


    def __iter__(self) -> Iter:
        return self


    def all_(self, f: Callable) -> bool:
        return all(item.map(f).value for item in self)


    def any(self, f: Callable) -> bool:
        return any(item.map(f).value for item in self)


    def map(self, f: Callable) -> Iter:
        return Iter(item.map(f).value for item in self)


    def filter(self, pred: Union[None, Callable]) -> Iter:
        pred = bool if pred is None else pred
        return Iter(filter(pred, (opt.value for opt in self)))


    def filter_map(self, f: Callable) -> Iter:
        """
        Note, the closure supplied here **must** return
        Option
        """
        def filter_mapper(self, f):
            for item in self:
                val = f(item.value)

                if val.is_some():
                    yield val.value

        return Iter(filter_mapper(self, f))


    def flat_map(self, f: Callable) -> Iter:
        def flat_mapper(self, f):
            for item in self:
                yield from map(f, item.value)

        return Iter(flat_mapper(self, f))


    def flatten(self: Iter) -> Iter:
        def flat(self):
            for item in self:
                yield from item.value

        return Iter(flat(self))


    def inspect(self, f: Callable) -> Iter:
        def inspector(self, f):
            for item in self:
                f(item.value)
                yield item.value

        return Iter(inspector(self, f))


    def collect(self, type_: Callable) -> Container[T]:
        return type_((item.unwrap() for item in self))


    def next(self) -> Option:
        return Option(next(self.iter_, None))


    def chain(self, iter_) -> Iter:
        def chained_iterator(left, right):
            yield from (item.value for item in left)

            if not isinstance(right, Iter):
                if not isinstance(right, Iterator):
                    right = Iter(iter(right))
                else:
                    right = Iter(right)

            yield from (item.value for item in right)

        return Iter(chained_iterator(self, iter_))


    def count(self) -> int:
        return sum(1 for i in self)


    def last(self) -> Option:
        # if iterator is consumed, yield from will just not
        # iterate, so I need it to at least yield an Option(None)
        def peeked_iterator(iterator):
            yield iterator.next()

            yield from iterator

        for item in peeked_iterator(self):
            continue

        return item


    def advance_by(self, n) -> int:
        i = sum(1 for _ in islice(self, n))

        return i


    def nth(self, n) -> Option:
        consume(self, n-1)

        return self.next()


    def step_by(self, n) -> Iter:
        def stepper(n):
            for i, item in enumerate(self):
                if not i % n:
                    yield item.value


        # a spicier version might be
        new_stepper = map(itemgetter(1), filter(lambda x: not x[0] % n, enumerate(self)))

        return Iter(stepper(n))


    def zip(self, other) -> Iter:
        return Iter((a.value, b.value) for a, b in zip(self, Iter(other)))


    def enumerate(self, start=0) -> Iter:
        return Iter((i, item.value) for i, item in enumerate(self, start=start))


    def peek(self) -> Option:
        def plain_iterator(val, self):
            yield val.unwrap()
            yield from (item.value for item in self)

        val = self.next()

        if val.is_some():
            self.iter_ = plain_iterator(val, self)

        return val


    def skip_while(self, f: Callable) -> Iter:
        while True:
            item = self.next()
            if item.is_some() and f(item.value):
                continue
            else:
                break

        return self


    def take_while(self, f: Callable) -> Iter:
        def taker():
            while True:
                val = self.next()
                pred = f(val.value) if val.is_some() else False
                if pred:
                    yield val
                else:
                    break

        return Iter((item.value for item in taker()))


    def find(self, f: Callable) -> Option:
        return self.filter(f).next()


    def find_map(self, f: Callable) -> Option:
        return self.filter_map(f).next()


    def fold(self, initial_value: T, f: Callable) -> T:
        return reduce(initial_value, (f(item.unwrap()) for item in self))
