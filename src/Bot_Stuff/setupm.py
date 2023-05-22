import typing as t
from functools import update_wrapper

F = t.TypeVar("F", bound=t.Callable[..., t.Any])

def setupmethod(f):
    f_name = f.__name__

    def wrapper_func(self, *args: t.Any, **kwargs: t.Any) -> t.Any:
        return f(self, *args, **kwargs)

    return t.cast(F, update_wrapper(wrapper_func, f))