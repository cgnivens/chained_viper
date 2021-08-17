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

### Lazy Options
For truly lazy options, use the `Option.iter()` method to change it into an iterator over the wrapped value. For non-iterable values such as `int`, `bool`, `float`, etc, this will result in a single-element iterator over `(value, )`. Otherwise, it will iterate over the wrapped value itself. However, applying functions through `map`s and `filter`s will be truly lazy and will not be called until `.next`, `.peek`, or `.collect` is called on the iterator:

```python
from time import sleep
from chained_viper import Option

def f(x):
    print("Some long function call")
    sleep(5)
    x += 1
    print("Modified x")
    sleep(3)
    return x


# function not applied here
my_iter = Option(5).iter().map(f)

# but it is applied here
new_value = my_iter.next()
Some long function call
Modified x

assert new_value == Option(6)
```
Otherwise, `Option.map`/`Option.filter`/... is greedy, and will evaluate immediately.
