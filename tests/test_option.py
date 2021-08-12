from chained_viper import Iter, Option, Result
import pytest


def sanity_check():
    assert True



def test_is_some():
    assert Option(True).is_some()
    assert not Option(True).is_none()


def test_is_none():
    assert Option(None).is_none()
    assert not Option(None).is_some()


def test_unwrap_not_none():
    o = Option(True)
    assert o.is_some()
    assert o.unwrap() is True


def test_unwrap_none_raises_exception():
    o = Option(None)

    with pytest.raises(ValueError):
        o.unwrap()



def test_unwrap_or():
    o = Option(1).unwrap_or("Err")
    assert o == 1

    o = Option(None).unwrap_or("Err")
    assert o == "Err"


def test_unwrap_or_else():
    o = Option(1)

    assert o.unwrap_or_else(lambda: "Err") == 1

    o = Option(None).unwrap_or_else(lambda: "Err")
    assert o == "Err"


def test_map():
    o = Option(1).map(lambda x: x+1)
    assert o.is_some()
    assert o == Option(2)


def test_map_or():
    o = Option(1).map_or(lambda x: x+1, 6)
    assert o.is_some()
    assert o == Option(2)

    o = Option(None).map_or(lambda x: x+1, 6)
    assert o.is_some()
    assert o == Option(6)


    o = Option(1).map_or(lambda x: None, 6)
    assert o.is_none()
    assert o == Option(None)


def test_map_or_else():
    o = Option(1).map_or_else(lambda x: x+1, lambda: f"uh oh")
    assert o.is_some()
    assert o == Option(2)

    o = Option(None).map_or_else(lambda x: x+1, lambda: f"uh oh")
    assert o.is_some()
    assert o == Option("uh oh")



def test_ok_or():
    r = Option(1).ok_or(Exception("Bad thing"))
    print(r)
    assert r.is_ok()
    assert not r.is_err()
    assert r.unwrap() == 1

    err = Exception
    r = Option(None).ok_or(err("Bad thing"))
    assert not r.is_ok()
    assert r.is_err()

    with pytest.raises(err):
        r.unwrap()
