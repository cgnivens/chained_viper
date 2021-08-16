from chained_viper import Result, Option, Iter
import pytest


def test_sanity():
    assert True


@pytest.fixture
def ok():
    return Result(True)


@pytest.fixture
def err():
    return Result(Exception("bad"))



def test_is_ok(ok, err):
    assert ok.is_ok()
    assert Result("Some value").is_ok()
    assert not err.is_ok()
    assert not Result(Exception("Some value")).is_ok()



def test_is_err(ok, err):
    assert not ok.is_err()
    assert err.is_err()
    assert not Result("Some value").is_err()
    assert Result(Exception("Some value")).is_err()



def test_into():
    # test ok
    r = Result.into(lambda: True)
    assert r.is_ok()
    assert r == Result(True)

    def function_raises():
        raise Exception("raised by function")


    r = Result.into(function_raises)
    assert r.is_err()
    assert r == Result(Exception("raised by function"))


def test_map(ok, err):
    r = ok.map(lambda x: x + 1)
    assert r == Result(2)

    e = err.map(lambda x: x + 1)
    assert e == err

    e = ok.map(lambda x: Exception(x))
    assert e.is_err()
    assert e == Result(Exception(True))



def test_map_or():
    r = Result(1).map_or(lambda x: x + 1, 3)
    assert r == Result(2)

    r = Result(Exception(1)).map_or(lambda x: x+1, 3)
    assert r == Result(3)



def test_map_or_else():
    r = Result(1).map_or_else(lambda x: x + 1, lambda x: 42)
    assert r == Result(2)

    r = Result(Exception(1)).map_or_else(lambda x: x + 1, lambda x: 42)
    assert r == Result(42)


def test_map_err(ok, err):
    r = ok.map_err(lambda x: x+1)
    assert r == ok

    r = err.map_err(lambda x: len(x))
    assert r == Result(3)



def test_unwrap(ok, err):
    assert ok.unwrap()

    with pytest.raises(Exception):
        err.unwrap()



def test_ok():
    assert Result(True).ok().is_some()
    assert Result(None).ok().is_none()
    assert Result(Exception("val")).ok().is_none()



def test_err(ok, err):
    assert ok.err().is_none()
    assert err.err().is_some()



def test_iter():
    iterator = Result('abc').iter_()
    assert iterator.next() == Option('a')

    iterator = Result(True).iter_()
    assert iterator.next() == Option(True)

    iterator = Result([]).iter_()
    assert iterator.next() == Option(None)


def test_and_(err):
    r = Result("abc")
    assert r.and_(Result("def")) == Result("def")

    assert err.and_(Result("def")) == err

    assert r.and_(err) == err



def test_and_then(ok, err):
    assert ok.and_then(lambda x: x + 1) == Result(2)
    assert err.and_then(lambda x: x + 1) == err



def test_or_(ok, err):
    r = Result(2)
    assert ok.or_(r) == ok
    assert err.or_(r) == r
    assert ok.or_(err) == ok


def test_or_else(ok, err):
    assert ok.or_else(lambda x: x + 1) == ok
    assert err.or_else(lambda x: len(x)) == Result(3)


def test_unwrap_or(ok, err):
    assert ok.unwrap_or(False)
    assert not err.unwrap_or(False)



def test_unwrap_or_else(ok, err):
    assert ok.unwrap_or_else(lambda x: False)
    assert err.unwrap_or_else(lambda x: 42) == 42


def test_expect(ok, err):
    assert ok.expect("Hello") is True

    with pytest.raises(Exception):
        err.expect("Hello")


def test_expect_err(ok, err):
    assert err.expect_err("Got OK") == 'bad'

    with pytest.raises(Exception):
        ok.expect_err("Got OK")



def test_unwrap_err(ok, err):
    assert err.unwrap_err() == 'bad'

    with pytest.raises(Exception):
        ok.unwrap_err()
