from . import collections, irc

def irccmp(str1, str2):
    return irc.String(str1) == irc.String(str2)
