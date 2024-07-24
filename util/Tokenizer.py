__all__ = ['collapse_tokens', 'tokenize', 'TokenSet', 'Token']

import re
from bidict import bidict
from typing import NamedTuple, cast, Iterable, Iterator, Mapping, overload, Callable, AnyStr


class Token[T](NamedTuple):
    type: T
    value: str
    line: int
    column: int


class TokenSet:
    r'''A set of tokens, specified as a list of tuples of the form: [token_name, token_regex_str]
    An example tokenset:
    keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
        ('ASSIGN',   r':='),           # Assignment operator
        ('END',      r';'),            # Statement terminator
        ('ID',       r'[A-Za-z]+'),    # Identifiers
        ('OP',       r'[+\-*/]'),      # Arithmetic operators
        ('NEWLINE',  r'\n'),           # Line endings
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character
    ]
    '''
    def __init__(self, token_specification: list[tuple[str,str]], keywords: set[str]=set(), re_flags=re.NOFLAG):
        self.spec = token_specification
        self.keywords = keywords
        self.token_ids: bidict[int,str] = bidict()
        for i, (name,_) in enumerate(token_specification):
            self.token_ids[i] = name
        offset = len(self.spec)
        for i, keyword in enumerate(keywords):
            self.token_ids[i+offset] = keyword
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        self.regex = cast(re.Pattern[str], re.compile(tok_regex, re_flags))


    @overload
    def tokenize(self, code: str) -> Iterator[Token[str]]: ...
    @overload
    def tokenize[T](self, code: str, mapping: Mapping[str,T]|Callable[[str],T|None]) -> Iterator[Token[T]]: ...

    def tokenize[T](self, code, mapping: Mapping[str,T]|Callable[[str],T|None]|None = None) -> Iterator[Token]:
        return tokenize(code, self.regex, keywords=self.keywords, mapping=mapping) #type:ignore

def default_name(name: str) -> str:
    return name
def map_name[T](mapping: Mapping[str,T]) -> Callable[[str],T|None]:
    default = mapping.get("", None)
    def get(name: str) -> T|None:
        return mapping.get(name, default)
    return get

@overload
def tokenize(code: str, tok_regex: re.Pattern[str],*, keywords: set[str]=set()) -> Iterator[Token[str]]: ...
@overload
def tokenize[T](code: str, tok_regex: re.Pattern[str],*, keywords: set[str]=set(), mapping: Mapping[str,T]|Callable[[str],T|None]) -> Iterator[Token[T]]: ...

def tokenize[T](code: str, tok_regex: re.Pattern[str],*, keywords: set[str]=set(), mapping: Mapping[str,T]|Callable[[str],T|None]|None=None) -> Iterator[Token]:
    line_num = 1
    line_start = 0
    last_end = 0
    namefunc = default_name if mapping is None else (map_name(mapping) if isinstance(mapping, Mapping) else mapping)
    skipped_name = namefunc("")
    yield_skipped = skipped_name is not None

    for mo in re.finditer(tok_regex, code):
        kind = namefunc(mo.lastgroup)  # type: ignore
        if kind is None:
            continue
        if yield_skipped and last_end < mo.start():
            yield Token(skipped_name, code[last_end:mo.start()], line_num, line_start)

        line_num, line_start = _update_linecol(code, last_end, mo.start(), line_num, line_start)
        value = mo.group()
        line = line_num
        column = mo.start() - line_start
        line_num, line_start = _update_linecol(code, mo.start(), mo.end(), line_num, line_start)
        last_end = mo.end()
        if value in keywords:
            kind = namefunc(value)
        yield Token(kind, value, line, column)

    if yield_skipped and last_end < len(code):
        yield Token(skipped_name, code[last_end:], line_num, line_start)


def _update_linecol(string, start, end, line_no, line_start) -> tuple[int,int]:
    newlines = string.count('\n', start,end)
    if newlines > 0:
        line_start = string.rfind('\n', start, end) + 1
    return (newlines+line_no, line_start)


def collapse_tokens[T](tokens: Iterable[Token[T]], types: set[T]|T, to: T|None=None) -> Iterator[Token[T]]:
    if not isinstance(types, set):
        types = set(types) # type: ignore
    collapsed = ""
    line = 0
    col = 0
    new_type = None
    for token in tokens:
        if token.type in types:
            if new_type is None:
                new_type = to if to is not None else token.type
                line = token.line
                col = token.column
            collapsed += token.value
        else:
            if new_type is not None:
                yield Token(new_type, collapsed, line, col)
                collapsed = ''
                new_type = None
            yield token
    if new_type is not None:
        yield Token(new_type, collapsed, line, col)

