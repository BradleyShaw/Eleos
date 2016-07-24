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
        super(Dict, self).__setitem__(key, value)

    def __getitem__(self, key):
        key = self.ircize_key(key)
        super(Dict, self).__getitem__(key)

    def __contains__(self, key):
        key = self.ircize_key(key)
        super(Dict, self).__contains__(key)

    def __delitem__(self, key):
        key = self.ircize_key(key)
        super(Dict, self).__delitem__(key)

    def get(self, key, *args, **kwargs):
        key = self.ircize_key(key)
        super(Dict, self).get(key, *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        key = self.ircize_key(key)
        super(Dict, self).setdefault(key, *args, **kwargs)

    def pop(self, key, *args, **kwargs):
        key = self.ircize_key(key)
        super(Dict, self).pop(key, *args, **kwargs)

    @staticmethod
    def ircize_key(key):
        if isinstance(key, six.string_types):
            key = String(key)
        return key
