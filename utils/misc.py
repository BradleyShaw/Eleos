import binascii
import socket

from . import irc


def irccmp(str1, str2):
    return irc.String(str1) == irc.String(str2)


def listreplace(lst, old, new):
    for i, v in enumerate(lst):
        if v == old:
            lst.pop(i)
            lst.insert(i, new)


def count(item, singular, plural):
    return "{0} {1}".format(item, singular if int(item) == 1 else plural)


def hex2ip(hexip):
    hexip = binascii.unhexlify(hexip)
    return socket.inet_ntoa(hexip)
