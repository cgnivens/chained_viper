# Chained Viper
A ridiculous name for a needless module, but it's a functional-ish library for python. Want functional iterators? Options? Results? Monad-ish things? Here you go, with no guarantees or expectations of quality. It's more of an exercise, but if someone uses it, feel free to send bugs my way.


## Requirements
It has no external dependencies except for python3.6+. To install it:

```bash
python setup.py install
```

Since this isn't exactly a PyPI module.


## Tests
To run tests, you will need `pytest`:
```bash
python -m pip install pytest
python -m pytest
```

## Basics
### Option
A wrapper type for encompassing `Some` and `None` as options. I need to sort out the actual implementation as far as creating them, IMO it might be a bit easier to do `Some(type)` which returns `Option(type)`. Basically, create an option by directly calling the class on any type of value:

```python
from chained_viper import Option

some = Option(4)

# do some operations that return more options
print(some.map(lambda x: x + 5) == Option(9))
True

# Allows you to check explicit values
some.contains(4)
True

# unwrapping None will cause errors
Option(None).unwrap()
 ValueError: Bare 'None' not allowed

some.is_some()
True

some.is_none()
False


# Enables pipelining of good and bad values
Option(None).map_or_else(lambda x: x + 1, lambda: 42).unwrap()


# can convert to other types
Option(None).ok_or(Exception("Bad value")) == Result(Exception("Bad value"))

Option(1).iter().next() == Option(1)
```
