
from typing import Callable, Union, Any, Iterator, Generator, Tuple, TypeVar, Container
from enum import Enum
from copy import deepcopy
from .utils import consume
from itertools import islice
from functools import partial, reduce


T = TypeVar('T')
Option = T


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
