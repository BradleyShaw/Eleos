import string
import six

class String(six.text_type):
    translation = str.maketrans(
        string.ascii_uppercase + r"[]\^",
        string.ascii_lowercase + r"{}|~"
    )

    def __lt__(self, other):
        return self.lower() < other.lower()

    def __gt__(self, other):
        return self.lower() > other.lower()

    def __eq__(self, other):
        return self.lower() == other.lower()

    def __hash__(self):
        return hash(self.lower())

    def lower(self):
        return (
            self.translate(self.translation) if self
            else super(String, self).lower()
        )

    def index(self, sub):
        return self.lower().index(sub.lower())

    def split(self, splitter=' ', maxsplit=0):
        pattern = re.compile(re.escape(splitter), re.I)
        return pattern.split(self, maxsplit)

class Dict(dict):

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__()
        d = dict(*args, **kwargs)
        for item in d.items():
            self.__setitem__(*item)

    def __setitem__(self, key, value):
        key = self.ircize_key(key)
        return super(Dict, self).__setitem__(key, value)

    def __getitem__(self, key):
        key = self.ircize_key(key)
        return super(Dict, self).__getitem__(key)

    def __contains__(self, key):
        key = self.ircize_key(key)
        return super(Dict, self).__contains__(key)

    def __delitem__(self, key):
        key = self.ircize_key(key)
        return super(Dict, self).__delitem__(key)

    def get(self, key, *args, **kwargs):
        key = self.ircize_key(key)
        return super(Dict, self).get(key, *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        key = self.ircize_key(key)
        return super(Dict, self).setdefault(key, *args, **kwargs)

    def pop(self, key, *args, **kwargs):
        key = self.ircize_key(key)
        return super(Dict, self).pop(key, *args, **kwargs)

    @staticmethod
    def ircize_key(key):
        if isinstance(key, six.string_types):
            key = String(key)
        return key

class List(list):

    def __init__(self, *args, **kwargs):
        super(List, self).__init__()
        l = list(*args, **kwargs)
        for item in l:
            self.append(item)

    def __contains__(self, item):
        item = self.ircize_item(item)
        return super(List, self).__contains__(item)

    def __delitem__(self, item):
        item = self.ircize_item(item)
        return super(List, self).__delitem__(item)

    def append(self, item):
        item = self.ircize_item(item)
        return super(List, self).append(item)

    def insert(self, pos, item):
        item = self.ircize_item(item)
        return super(List, self).append(pos, item)

    def remove(self, item):
        item = self.ircize_item(item)
        return super(List, self).remove(item)

    def index(self, item):
        item = self.ircize_item(item)
        return super(List, self).index(item)

    def count(self, item):
        item = self.ircize_item(item)
        return super(List, self).count(item)

    @staticmethod
    def ircize_item(item):
        if isinstance(item, six.string_types):
            item = String(item)
        return item
