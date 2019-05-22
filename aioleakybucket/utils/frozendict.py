import collections.abc


BRACKETS = ('<', '>')


class FrozenDict(collections.abc.Mapping):
    _api_version = 0
    _old_api_loaders = {}

    __slots__ = ('_d', '_hash', '_fmt', '__weakref__')

    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None
        self._fmt = None

    def __getstate__(self):
        return (self._api_version, self._d)

    def __setstate__(self, state):
        api_version, *data = state

        if api_version == self._api_version:
            self._d = data[0]
        else:
            self._old_api_loaders[api_version](self, data)

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = 0
            for pair in self.items():
                self._hash ^= hash(pair)
        return self._hash

    def __eq__(self, other):
        if isinstance(other, FrozenDict):
            return self._d == other._d
        else:
            return self._d == other

    def __repr__(self):
        return repr(self._d)[1:-1].join(BRACKETS)

    def format(self, key_func=str, value_func=str,
               joinstr=',', key_value_format='{}={}'):
        if self._fmt is None:
            self._fmt = joinstr.join(
                key_value_format.format(k, v)
                for k, v in sorted(
                    (key_func(key), value_func(value))
                    for key, value in self._d.items()
                )
            )
        return self._fmt
