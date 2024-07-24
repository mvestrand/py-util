__all__ = ["expect_iter", "expect_list", "expect_one"]

from typing import Iterable, Iterator, overload, TypeGuard, reveal_type, Never
from types import EllipsisType, NoneType
import inspect
import os


@overload
def expect_iter[T](value: Iterable[T]) -> Iterator[T]: ...
@overload
def expect_iter(value: NoneType) -> Iterator[Never]: ...
@overload
def expect_iter[T](value: T) -> Iterator[T]: ...

def expect_iter(value) -> Iterator:
    if isinstance(value, Iterable):
        yield from value
    elif value is not None:
        yield value
        
def expect_list(value):
    if isinstance(value, Iterable):
        return list(value)
    elif value is not None:
        return [value]
    else:
        return []

@overload
def expect_one[T: (str,bytes,dict,bytearray,memoryview)](value: T, /) -> T: ...
@overload
def expect_one[T](value: Iterable[T], /) -> T: ...
@overload
def expect_one[D](value: Iterable[Never], default: D, /) -> D: ...
@overload
def expect_one[T,D](value: Iterable[T], default: D, /) -> T|D: ...
@overload
def expect_one(value: NoneType, /) -> Never: ...
@overload
def expect_one[D](value: NoneType, default: D, /) -> D: ...
@overload
def expect_one[T](value: T, /) -> T: ...


def expect_one(value, default=..., strict=True):
    first = value
    if isinstance(value, (str, bytes, dict, bytearray, memoryview)):
        return value
    elif isinstance(value, Iterable):
        i = value if isinstance(value, Iterator) else iter(value)
        first = next(i, None)
        if strict:
            second = next(i, None)
            assert second is None, f"Expected one value, received: {type(value)} [{first}, {second}, ...]"
    elif value is not None:
        return value
    
    # Error checking
    if first is None:
        if default == ...:
            raise ValueError(f"Expected one value, received empty: {type(value)} {str(value)}")
        return default
    return first


def __dir__():
    return sorted(__all__)