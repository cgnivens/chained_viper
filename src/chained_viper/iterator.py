from typing import Callable, Union, Any, Iterator
from enum import Enum
from copy import deepcopy
try:
    from .option import Option
except:
    from option import Option


class Iter:
    def __init__(self, iterator):
        self.iter_ = iterator


    def __next__(self):
        return self.next()


    def __iter__(self):
        return self


    def map_(self, f: Callable):
        return Iter((f(opt.value) for opt in self))


    def filter_(self, pred: Union[None, Callable]):
        pred = bool if pred is None else pred
        return Iter(filter(pred, (opt.value for opt in self)))


    def collect(self, type_):
        return type_((item.unwrap() for item in self))


    def next(self, *args):
        return Option(next(self.iter_, *args))


    def chain(self, iter_):
        def chained_iterator(left, right):
            yield from (item.unwrap() for item in left)

            if not isinstance(right, Iter):
                if not isinstance(right, Iterator):
                    right = Iter(iter(right))
                else:
                    right = Iter(right)

            yield from (item.unwrap() for item in right)

        return Iter(chained_iterator(self, iter_))


    def count(self):
        return sum(1 for i in self)


    def last(self):
        # if iterator is consumed
        def peeked_iterator(iterator):
            try:
                item = iterator.next()
            except:
                yield Option(None)

            yield from iterator

        for item in peeked_iterator(self):
            continue

        return item


    def advance_by(self, n):
        i = 0

        for _, (i, item) in zip(range(n), enumerate(self, start=1)):
            continue

        return i


    def nth(self, n):
        for item, i in zip(self, range(1, n+1)):
            continue

        return Option(item if i == n else None)




class TestIter:
    def __iter__(self):
        return self

    def __next__(self):
        return self.next()


    def __init__(self, iterator):
        self.iterator = iterator


    def next(self):
        return next(self.iterator, None)
