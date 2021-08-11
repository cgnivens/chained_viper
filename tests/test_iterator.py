from functional_python import Iter, Option
import pytest

def sanity_check():
    assert True

@pytest.fixture
def test_iterator():
    return Iter((True for i in range(10)))


@pytest.fixture
def range_iterator():
    return Iter(iter(range(10)))


def test_iteration(test_iterator):
    for item in test_iterator:
        assert item.is_some()
        assert item.unwrap()

    assert True


def test_items_are_options(test_iterator):
    for item in test_iterator:
        assert isinstance(item, Option)
        assert item.unwrap()


def test_iter_next(test_iterator):
    assert test_iterator.next().is_some()

    # consume iterator
    _ = [item for item in test_iterator]

    assert test_iterator.next().is_none()


def test_iter_last(range_iterator):
    item = range_iterator.last()
    assert item.is_some()
    assert item.unwrap() == 9



def test_iter_map(range_iterator):
    new_iterator = range_iterator.map(str)
    val = new_iterator.next()
    print(val)
    assert val == Option('0')


def test_iter_filter(range_iterator):
    new_iterator = range_iterator.filter(lambda x: x != 5)

    for item in new_iterator:
        assert item.is_some()
        assert item.unwrap() != 5


def test_iter_chain():
    left = Iter('abc')
    right = Iter('cba')

    assert left.chain(right).collect(list) == list('abccba')

    # test chain on non-iter
    left = Iter('abc')
    left.chain('cba').collect(list) == list('abccba')


def test_iter_chain_empty(range_iterator):
    assert range_iterator.chain([]).last().unwrap() == 9
    assert range_iterator.chain(Iter([])).last().is_none()


def test_iter_collect(range_iterator):
    val = range_iterator.collect(list)

    assert isinstance(val, list)
    assert val == list(range(10))


def test_iter_count(range_iterator):
    assert range_iterator.count() == 10


def test_iter_advance_by_in_range(range_iterator):
    steps = range_iterator.advance_by(2)
    assert steps == 2
    assert range_iterator.next().unwrap() == 2



def test_iter_advance_by_out_of_range(range_iterator):
    steps = range_iterator.advance_by(11)
    assert steps == 10
    assert range_iterator.next().is_none()



def test_find(range_iterator):
    val = range_iterator.find(lambda x: x == 5)
    assert val.is_some()
    val = range_iterator.find(lambda x: x == 2)
    assert val.is_none()


def test_find_map(range_iterator):
    val = range_iterator.find_map(lambda x: Option(x if x == 9 else None))
    assert val.is_some()
    assert val.unwrap() == 9

    val = range_iterator.find_map(lambda x: Option(x if x == 9 else None))
    assert val.is_none()


def test_peek(range_iterator):
    assert range_iterator.peek().unwrap() == 0
    assert range_iterator.next().unwrap() == 0


def test_nth(range_iterator):
    val = range_iterator.nth(4)
    print(val)
    assert val == Option(3)

    val = Iter('abcd').nth(3)
    assert val == Option('c')

    # iterator is exhausted
    assert range_iterator.nth(10).is_none()


def test_all(test_iterator):
    assert test_iterator.all_(bool)
