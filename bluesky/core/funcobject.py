import os
import inspect


class FuncObjectMeta(type):
    def __call__(cls, func, *args, **kwargs):
        return getattr(inspect.unwrap(func),
            '__func_object__',
            super().__call__(func, *args, **kwargs)
        )


class FuncObject(metaclass=FuncObjectMeta):
    ''' Function reference object that is automatically updated
        on implementation selectdion for replaceables, and on creation of
        instances.
    '''
    __slots__ = ['func', 'callback']

    def __init__(self, func) -> None:
        self.update(func.__func__ if isinstance(func, (staticmethod, classmethod)) else func)
        ufunc = inspect.unwrap(func)
        setattr(getattr(ufunc, '__func__', ufunc), '__func_object__', self)

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def __repr__(self) -> str:
        return repr(self.func)

    def notimplemented(self, *args, **kwargs):
        pass

    def update(self, func):
        self.func = func
        self.callback = func if self.valid else self.notimplemented

    def info(self):
        msg = ''
        if self.func.__name__ == '<lambda>':
            msg += 'Anonymous (lambda) function, implemented in '
        else:
            msg += f'Function {self.func.__name__}(), implemented in '
        if hasattr(self.func, '__code__'):
            fname = self.func.__code__.co_filename
            fname_stripped = fname.replace(os.getcwd(), '').lstrip('/')
            firstline = self.func.__code__.co_firstlineno
            msg += f'<a href="file://{fname}">{fname_stripped} on line {firstline}</a>'
        else:
            msg += f'module {self.func.__module__}'

        return msg

    @property
    def __wrapped__(self):
        return self.func

    @property
    def __name__(self):
        return self.func.__name__

    @property
    def valid(self):
        if self.func is None:
            return False
        spec = inspect.signature(self.func)
        # Check if this is an unbound class/instance method
        return spec.parameters.get('self') is None and \
            spec.parameters.get('cls') is None
