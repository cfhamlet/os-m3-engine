from .common import Configurable


class Driver(Configurable):

    def __init__(self, config, current_thread):
        super(Driver, self).__init__(config)
        self._current_thead = current_thread

    @property
    def current_thread(self):
        return self._current_thead

    @property
    def runtime_context(self):
        return self.config.runtime_context

    def run(self):
        raise NotImplementedError
