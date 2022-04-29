import json

class OnChangeDict(dict):
    """
    dict with changed flag
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hash = self._hash()

    def _hash(self):
        return hash(json.dumps(self, sort_keys=True))

    @property
    def changed(self):
        return self.hash != self._hash()

    def clear_changed(self):
        self.hash = self._hash()