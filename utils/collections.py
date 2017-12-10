import collections
import string
import six
import re


class String(six.text_type):
    casemapping = {
        'upper': string.ascii_uppercase,
        'lower': string.ascii_lowercase
    }

    def __lt__(self, other):
        return self.lower() < other.lower()

    def __gt__(self, other):
        return self.lower() > other.lower()

    def __eq__(self, other):
        return self.lower() == other.lower()

    def __hash__(self):
        return hash(self.lower())

    def lower(self):
        translation = str.maketrans(
            self.casemapping['upper'],
            self.casemapping['lower']
        )
        return (
            self.translate(translation) if self
            else super(String, self).lower()
        )

    def upper(self):
        translation = str.maketrans(
            self.casemapping['lower'],
            self.casemapping['upper']
        )
        return (
            self.translate(translation) if self
            else super(String, self).lower()
        )

    def index(self, sub):
        return self.lower().index(sub.lower())

    def split(self, splitter=' ', maxsplit=0):
        pattern = re.compile(re.escape(splitter), re.I)
        return List(pattern.split(self, maxsplit))


class Dict(dict):
    @staticmethod
    def transform_key(key):
        if isinstance(key, six.string_types):
            key = String(key)
        return key

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__()
        d = dict(*args, **kwargs)
        for item in d.items():
            self.__setitem__(*item)

    def __setitem__(self, key, value):
        key = self.transform_key(key)
        return super(Dict, self).__setitem__(key, value)

    def __getitem__(self, key):
        key = self.transform_key(key)
        return super(Dict, self).__getitem__(key)

    def __contains__(self, key):
        key = self.transform_key(key)
        return super(Dict, self).__contains__(key)

    def __delitem__(self, key):
        key = self.transform_key(key)
        return super(Dict, self).__delitem__(key)

    def get(self, key, *args, **kwargs):
        key = self.transform_key(key)
        return super(Dict, self).get(key, *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        key = self.transform_key(key)
        return super(Dict, self).setdefault(key, *args, **kwargs)

    def pop(self, key, *args, **kwargs):
        key = self.transform_key(key)
        return super(Dict, self).pop(key, *args, **kwargs)


class List(list):
    @staticmethod
    def transform_item(item):
        if isinstance(item, six.string_types):
            item = String(item)
        return item

    def __init__(self, *args, **kwargs):
        super(List, self).__init__()
        _l = list(*args, **kwargs)
        for item in _l:
            self.append(item)

    def __contains__(self, item):
        item = self.transform_item(item)
        return super(List, self).__contains__(item)

    def __delitem__(self, item):
        item = self.transform_item(item)
        return super(List, self).__delitem__(item)

    def append(self, item):
        item = self.transform_item(item)
        return super(List, self).append(item)

    def insert(self, pos, item):
        item = self.transform_item(item)
        return super(List, self).insert(pos, item)

    def remove(self, item):
        item = self.transform_item(item)
        return super(List, self).remove(item)

    def index(self, item):
        item = self.transform_item(item)
        return super(List, self).index(item)

    def count(self, item):
        item = self.transform_item(item)
        return super(List, self).count(item)


class OrderedDict(collections.OrderedDict):
    @staticmethod
    def transform_key(key):
        if isinstance(key, six.string_types):
            key = String(key)
        return key

    def __init__(self, *args, **kwargs):
        super(OrderedDict, self).__init__()
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
        key = self.transform_key(key)
        return super(OrderedDict, self).__setitem__(key, value)

    def __getitem__(self, key):
        key = self.transform_key(key)
        return super(OrderedDict, self).__getitem__(key)

    def __contains__(self, key):
        key = self.transform_key(key)
        return super(OrderedDict, self).__contains__(key)

    def __delitem__(self, key):
        key = self.transform_key(key)
        return super(OrderedDict, self).__delitem__(key)

    def __repr__(self):
        return repr(dict(self))

    def get(self, key, *args, **kwargs):
        key = self.transform_key(key)
        return super(OrderedDict, self).get(key, *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        key = self.transform_key(key)
        return super(OrderedDict, self).setdefault(key, *args, **kwargs)

    def pop(self, key, *args, **kwargs):
        key = self.transform_key(key)
        return super(OrderedDict, self).pop(key, *args, **kwargs)
