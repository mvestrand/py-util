__all__ = ['tern', 'Ternary', 'strict_true', 'strict_false', 'maybe_true', 'maybe_false', 'true', 'false', 'maybe']

from enum import Enum

type tern = Ternary | bool

class Ternary(Enum):
    false = 0
    true = 1
    maybe = 2
    def __str__(self):
        if self is true: 
            return 'true'
        if self is false: 
            return 'false'
        return 'maybe'

    def __or__(self, other):
        if self is true:
            return true
        if not isinstance(other, Ternary):
            other = Ternary(bool(other))
        if self is false:
            return other
        if other is true:
            return true
        else:
            return maybe
    def __ror__(self, other): 
        return self.__or__(other)

    def __and__(self, other):
        if self is false:
            return false
        if not isinstance(other, Ternary):
            other = Ternary(bool(other))
        if self is true:
            return other
        if other is false:
            return false
        else:
            return maybe
    def __rand__(self, other): 
        return self.__and__(other)

    def __invert__(self):
        if self is true:
            return false
        if self is false:
            return true
        return maybe
    
    def __bool__(self): return NotImplemented


def strict_true(predicate):
    if predicate is true:
        return True
    if predicate is false or predicate is maybe:
        return False
    return bool(predicate)

def strict_false(predicate) -> bool:
    return not maybe_true(predicate)

def maybe_true(predicate):
    if predicate is true or predicate is maybe:
        return True
    if predicate is false:
        return False
    return bool(predicate)
def maybe_false(predicate) -> bool:
    return not strict_true(predicate)

false = Ternary.false
true = Ternary.true
maybe = Ternary.maybe

def __dir__():
    return sorted(__all__)
# print(f'{'A':^6}|{'B':^6}|{'A & B':^10}|{'B & A':^10}|{'A | B':^10}|{'B | A':^10}')
# for a in [true, false, maybe]:
#     print(f'{'-'*6}|{'-'*6}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}')
#     for b in [true, false, maybe]:
#         print(f'{a:^6}|{b:^6}|{a&b:^10}|{b&a:^10}|{a|b:^10}|{b|a:^10}')

# print()
# print(f'{'A':^6}|{'B':^6}|{'A & bool':^10}|{'bool & A':^10}|{'A | bool':^10}|{'bool | A':^10}')
# for a in [true, false, maybe]:
#     print(f'{'-'*6}|{'-'*6}|{'-'*10}|{'-'*10}|{'-'*10}|{'-'*10}')
#     for b in [True, False]:
#         print(f'{a:^6}|{b:^6}|{a&b:^10}|{b&a:^10}|{a|b:^10}|{b|a:^10}')
