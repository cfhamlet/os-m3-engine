import logging
import threading

from .common import Configurable


class Othread(Configurable, threading.Thread):

    def __init__(self, config, started, driver_cls, **kwargs):
        Configurable.__init__(self, config)
        threading.Thread.__init__(self, **kwargs)

        self._stopping = False
        self._started = started
        self._logger = logging.getLogger(self.name)
        self._driver_cls = driver_cls

    @property
    def runtime_context(self):
        return self.config.runtime_context

    def run(self):
        driver = None
        try:
            self._started.set()
            self._logger.debug('Start')
            driver = self._driver_cls(self.config, self)
            driver.run()
        except Exception as e:
            self._logger.error('Unexpected exception, %s' % str(e))
        self._logger.debug('Stop')

    def stopping(self):
        return self._stopping

    def stop(self):
        self._stopping = True


class OthreadManager(Configurable):
    def __init__(self, config, runtime_context, thread_cls, thread_num, driver_cls):
        super(OthreadManager, self).__init__(config)
        started = threading.Event()
        self._started = started
        self._threads = [thread_cls(config, started, driver_cls, name='%s.%d' % (
            thread_cls.__name__, i)) for i in range(0, thread_num)]

    def start(self):
        while not self._started.wait(0.1):
            if self._started.is_set():
                break
            list(map(lambda t: t.start(), self._threads))

    def setDaemon(self, daemonic):
        list(map(lambda t: t.setDaemon(daemonic), self._threads))

    def join(self):
        list(map(lambda t: t.join(), self._threads))

    def stop(self):
        list(map(lambda t: t.stop(), self._threads))

    def stopped(self):
        return not any([t.isAlive() for t in self._threads])
