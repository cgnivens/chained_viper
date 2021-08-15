from chained_viper import Result
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
