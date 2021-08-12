from .result import Result
from .option import Option
from .iterator import Iter

from . import iterator
from . import result
from . import option

iterator.Result = Result
option.Result = Result

option.Iter = Iter
result.Iter = Iter

iterator.Option = Option
result.Option = Option
