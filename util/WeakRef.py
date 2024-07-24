__all__ = ["WeakRef"]

import weakref
import typing as t

class WeakRef[T](weakref.ReferenceType[T]):
    __dead_ref: t.Self = None # type: ignore
    def __new__(cls, o: T, callback: t.Callable[[weakref.ReferenceType[T]], t.Any] | None = None, /) -> t.Self:
        if o is None:
            return cls.__dead_ref # type: ignore
        return super().__new__(cls, o, callback)
    def __init__(self, o: T, callback: t.Callable[[weakref.ReferenceType[T]], t.Any] | None = None, /):
        self.deref = None
        self.locks = 0
    def __bool__(self) -> bool: return self() is None
    def __eq__(self, other) -> bool: return self() == other()
    def __enter__(self):
        self.deref = self()
        self.locks += 1
        return weakref.proxy(self.deref) if self.deref is not None else None
    def __exit__(self, *args):
        self.locks -= 1
        if self.locks <= 0:
            self.deref = None
    @staticmethod
    def __create_dead_ref():
        if WeakRef.__dead_ref is None:
            class Dummy: pass
            WeakRef.__dead_ref = WeakRef(Dummy()) # type: ignore
            del Dummy
WeakRef._WeakRef__create_dead_ref() # type: ignore

