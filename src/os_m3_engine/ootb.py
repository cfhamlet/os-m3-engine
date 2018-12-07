import logging

from .common import binary_stdin
from .core.backend import Backend
from .core.frontend import Frontend
from .core.transport import Transport


class StdinFrontend(Frontend):
    def produce(self):
        for line in binary_stdin:
            yield line


class LogTransport(Transport):
    def setup(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def transport(self, data):
        self._logger.info(data)
        return data


class LogBackend(Backend):
    def setup(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def process(self, data):
        self._logger.info(data)
