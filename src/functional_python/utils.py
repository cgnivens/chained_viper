
from itertools import islice
from collections import deque


def consume(iterable, n=None):
    if n is None:
        deque(iterable, maxlen=0)
    else:
        next(islice(iterable, n, n), None)



class ZippedIterator:
    def __init__(self, iterator, other):
        self.iter_ = self.good_zip(iterator, other)


    def good_zip(self, iterator, other):
        while True:
            left, right = iterator.peek(), other.peek()

            if not left.is_some() and right.is_some():
                break
            else:
                yield left.next(), right.next()
