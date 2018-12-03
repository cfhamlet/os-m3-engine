
import sys
_PY3 = sys.version_info[0] == 3

if _PY3:
    import queue as Queue
else:
    import Queue


class Configurable(object):
    def __init__(self, config):
        self._config = config

    @property
    def config(self):
        return self._config


class RuntimeContext(object):
    pass
