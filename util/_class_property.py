from typing import Any, Callable


class inst_class_property(property):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_fget = None
    def __get__(self, instance: Any, owner: type | None = None, /) -> Any:
        if instance:     return super().__get__(instance, owner)
        if self.class_fget: return self.class_fget(owner)
        return self
    def class_getter(self, fget: Callable[[Any], Any], /) -> 'inst_class_property':
        self.class_fget = fget
        return self

class class_property(property):
    def __get__(self, instance: Any, owner: type | None = None, /) -> Any:
        if instance: return self.fget(instance.__class__) # type:ignore
        return self.fget(owner) # type: ignore


