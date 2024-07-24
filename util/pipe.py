__all__ = ["pipe","IterPipe","PipeChannel","P0","Transform",]

import itertools 
import more_itertools

from collections.abc import Callable, Iterable, Iterator, MutableSequence, MutableSet, MutableMapping
from typing import Any, Protocol, cast, runtime_checkable, overload, Self



class PipeChannel[T](Iterable[T]):
    def __init__(self, index: int):
        self.index = index
    def __iter__(self) -> Iterator[T]:
        return iter(())
    def __str__(self) -> str: return f'Channel[{self.index}]'
P0 = PipeChannel(0)


@runtime_checkable
class Transform[T,S](Protocol):
    def __call__(self, data: Iterable[T]) -> Iterator[S]: ...

class IterPipe[T](Iterator[T]):
    def __init__(self, data: Iterable[T]):
        self._data: Iterator[T] = iter(data)
    def __iter__(self):
        return self._data
    def __next__(self):
        return next(self._data)
    def mutate[S](self, data: Iterator[S]) -> 'IterPipe[S]':
        self._data = data               # type: ignore
        return self                     # type: ignore

    def __rshift__(self, other):
        if isinstance(other, (list, set)):
            return self.tee_lazy(other)
        if isinstance(other, Transform):
            return self.mutate(other(self._data))
        else:
            raise NotImplementedError(f'{type(self)} >> {type(other)} not supported')
    def __or__(self, other):
        if isinstance(other, Transform):
            return self.mutate(other(self._data))
        if isinstance(other, (set, list, tuple)):
            if len(other) == 0:
                raise ValueError
            return self.mutate(zip(
                *(itertools.starmap(f, cast(Iterable[Iterable[Any]], i)) 
                 for i, f in zip( itertools.tee(self._data,len(other)), 
                                  other))))


    @overload
    def map[S](self, func: Callable[[T], S], /) -> 'IterPipe[S]': ...
    @overload
    def map[T2,S](self, func: Callable[[T,T2], S], iter2: Iterator[T2], /) -> 'IterPipe[S]': ...
    @overload
    def map[T2,T3,S](self, func: Callable[[T,T2,T3], S], iter2: Iterator[T2], iter3: Iterator[T3],/) -> 'IterPipe[S]': ...
    @overload
    def map[T2,T3,T4,S](self, func: Callable[[T,T2,T3,T4], S], iter2: Iterator[T2], iter3: Iterator[T3], iter4: Iterator[T4],/) -> 'IterPipe[S]': ...
    @overload
    def map[T2,T3,T4,T5,S](self, func: Callable[[T,T2,T3,T4,T5], S], iter2: Iterator[T2], iter3: Iterator[T3], iter4: Iterator[T4], iter5: Iterator[T5],/) -> 'IterPipe[S]': ...
    def map[S](self, func: Callable[..., S], *args, **kwargs) -> 'IterPipe[S]':
        return self.mutate(map(func,self._data, *args, **kwargs))


    def filter(self, pred: Callable[[T],object]):
        return self.mutate(filter(pred, self._data))

    def accumulate(self, func, initial=None):
        return self.mutate(itertools.accumulate(self._data, func, initial=initial))
    def batched(self, n: int):
        return self.mutate(itertools.batched(self._data, n))
    def combinations(self, r: int):
        return self.mutate(itertools.combinations(self._data, r))
    def dropwhile(self, pred: Callable[[T],object]):
        return self.mutate(itertools.dropwhile(pred, self._data))
    def filterfalse(self, pred: Callable[[T],object]):
        return self.mutate(itertools.filterfalse(pred, self._data))
    def flatten(self):
        return self.mutate(itertools.chain.from_iterable(self._data)) #type: ignore
    def map_if(self, pred: Callable[[Any],bool], func: Callable[[Any],Any], func_else: Callable[[Any],Any]|None=None):
        return self.mutate(more_itertools.map_if(self._data, pred, func, func_else))
    def groupby(self, keyfunc=None):
        return self.mutate(itertools.groupby(self._data, keyfunc))
    def ds_map(self, func):
        return self.mutate(more_itertools.doublestarmap(func, self._data)) #type: ignore
    def starmap[S](self, func: Callable[..., S], /) -> 'IterPipe[S]':
        return self.mutate(itertools.starmap(func, cast(Iterable[Iterable[Any]], self._data)))
    def unique_everseen(self, key=None):
        seen = set()
        if key is None:
            for element in itertools.filterfalse(seen.__contains__, self._data):
                seen.add(element)
                yield element
        else:
            for element in self._data:
                k = key(element)
                if k not in seen:
                    seen.add(k)
                    yield element
    @overload
    def tee_lazy(self, target: MutableSequence[Iterator]|MutableSet[Iterator],/)-> Self: ...
    @overload
    def tee_lazy(self, target: MutableMapping[str,Iterator], name: str,/)-> Self: ...
    def tee_lazy(self, target, *args, **kwargs) -> Self:
            self._data, spare = itertools.tee(self._data,2)
            if isinstance(target, MutableMapping):
                target[args[0]] = spare
            elif isinstance(target, MutableSequence):
                target.append(spare)
            elif isinstance(target, MutableSet):
                target.add(spare)
            else:
                raise TypeError(f'type {type(target)} not supported by tee_lazy')
            return self


class WrappedTransform[T,S,**P](Transform[T,S]):
    def __init__(self, f: Callable[P,Iterable[S]], *args: P.args, **kwargs: P.kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs
    def __call__(self, data: Iterable[T]) -> Iterator[S]:
        L_args = tuple(itertools.takewhile(lambda x: not isinstance(x, PipeChannel), self.args))
        return self.f(*L_args, data, *self.args[len(L_args)+1:], **self.kwargs) #type: ignore

def pairwise():
    return WrappedTransform(itertools.pairwise, P0)


def pipe[T](data: Iterable[T]):
    return IterPipe[T](data)


def __dir__():
    return sorted(__all__)

# tees = []

# data = (
#     Pipe(range(20))
#     .filter(lambda x: x % 2 == 0)
#     .tee_into(tees)
#     .batched(2) >> tees
#     |  [lambda x, y: x*y,
#         lambda x, y: x/y,
#         lambda x, y: x**y]
#     )

# print(*data)
# print(*tees[0])
# print(*tees[1])