import string
import six
import re

from . import collections


class String(collections.String):
    casemapping = {
        'upper': string.ascii_uppercase + r'[]\^',
        'lower': string.ascii_lowercase + r'{}|~'
    }

    def split(self, splitter=' ', maxsplit=0):
        pattern = re.compile(re.escape(splitter), re.I)
        return List(pattern.split(self, maxsplit))


class Dict(collections.Dict):
    @staticmethod
    def transform_key(key):
        if isinstance(key, six.string_types):
            key = String(key)
        return key


class List(collections.List):
    @staticmethod
    def transform_item(item):
        if isinstance(item, six.string_types):
            item = String(item)
        return item


class OrderedDict(collections.OrderedDict):
    @staticmethod
    def transform_key(key):
        if isinstance(key, six.string_types):
            key = String(key)
        return key
