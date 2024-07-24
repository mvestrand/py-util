from typing import Iterable, overload

class Stack[T](list[T]):
    def push(self, *values: T):
        for value in values:
            self.append(value)
    @property
    def top(self): return self[-1]
    @top.setter
    def top(self, value): self[-1] = value
