import collections
import inspect

from .collections import String

events = []


def command(func=None, **kwargs):
    def wrapper(func):
        cmd = String(kwargs.get("command", func.__name__))
        events.append({
            "command": cmd,
            "help": mkhelp(cmd, inspect.getdoc(func)),
            "perms": {
                "global": kwargs.get("global_only", False),
                "flags": kwargs.get("flags", "A")
            },
            "event": "command",
            "func": func.__name__
        })
        return func
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper


def event(func=None, **kwargs):
    def wrapper(func):
        events.append({
            "type": String(kwargs.get("type", "ALL")),
            "event": "event",
            "func": func.__name__
        })
        return func
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper


def regex(func=None, **kwargs):
    def wrapper(func):
        events.append({
            "regex": kwargs.get("regex"),
            "event": "regex",
            "func": func.__name__
        })
        return func
    if isinstance(func, collections.Callable):
        return wrapper(func)
    return wrapper


def mkhelp(cmd, docstring):
    if docstring:
        docstring = docstring.splitlines()
        if len(docstring) > 1:
            syntax = docstring[0]
            desc = " ".join(docstring[1:]).strip()
            return "{0} {1} -- {2}".format(cmd, syntax, desc)
        else:
            syntax = docstring[0]
            return "{0} {1}".format(cmd, syntax)
    else:
        return "{0} has no help information.".format(cmd)
