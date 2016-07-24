import collections

events = []

def command(func=None, **kwargs):
    def wrapper(func):
        func._command = kwargs.get("command", func.__name__)
        func._help = func.__doc__
        func._flags = kwargs.get("flags", "A")
        func._event = "command"
        events.append(func)
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper

def event(func=None, **kwargs):
    def wrapper(func):
        func._type = kwargs.get("type", "ALL")
        func._event = "event"
        events.append(func)
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper

def regex(func=None, **kwargs):
    def wrapper(func):
        func._regex = kwargs.get("regex")
        func._event = "regex"
        events.append(func)
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper
