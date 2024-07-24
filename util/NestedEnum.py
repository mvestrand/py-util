from enum import Enum, EnumMeta
from typing import TYPE_CHECKING

class NestedEnum(Enum):
    def __new__(cls, *args):
        obj = object.__new__(cls)
        value = None
        # Normal Enumerator definition
        if len(args) == 1:
            value = args[0]

        # Have a tuple of values, first de value and next the nested enum (I will set in __init__ method)
        if len(args) == 2:
            value = args[0]

        if value:
            obj._value_ = value

        return obj

    def __init__(self, name, nested=None):
        if TYPE_CHECKING:
            self._nested = {}
        # At this point you can set any attribute what you want
        if nested:
            # Check if is an Enumerator you can comment this if. if you want another object
            if isinstance(nested, EnumMeta):

                for enm in nested:
                    # print(f"{type(self)}:{repr(self)}|{nested}|{enm}|{enm.name}")
                    self.__setattr__(enm.name, enm) # type: ignore


import enum
from enum import auto
from dataclasses import dataclass
from typing import cast, Any, reveal_type
from types import MethodType

class Data:
    def __init__(self, x):
        self.x = x

def printx(self):
    print(self.x)

cast(Any, Data).printx = MethodType(printx, Data)

class Term(Enum):
    LPAR = auto()
    RPAR = auto()
    A    = auto()
    PLUS = auto()
    END  = auto()
    INVALID = auto()
    

def member(value):
    def member_value(cls):
        if TYPE_CHECKING:
            return cls
        return value, cls
    return member_value


class Symbol(NestedEnum):
    @member(auto())
    class Term(Enum):
        LPAR = auto()
        RPAR = auto()
        A    = auto()
        PLUS = auto()
        END  = auto()
        INVALID = auto()
    @member(auto())
    class NTerm(Enum):
        S = auto()
        F = auto()

reveal_type(Symbol.Term)
repr(type(Symbol.Term))