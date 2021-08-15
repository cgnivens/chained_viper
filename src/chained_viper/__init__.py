from .result import Result
from .option import Option
from .iterator import Iter

from . import iterator
from . import result
from . import option

"""
This is a circular import hack, but I don't want
to stare at a 700+ line file with everything in it
"""

iterator.Result = Result
option.Result = Result

option.Iter = Iter
result.Iter = Iter

iterator.Option = Option
result.Option = Option
