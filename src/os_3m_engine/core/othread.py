import logging
import threading

from ..common import Configurable
from ..utils import load_class
from .driver import Driver


class Othread(Configurable, threading.Thread):

    def __init__(self, engine_config, runtime_context,
                 component_factory, start_trigger, stop_trigger, **kwargs):
        Configurable.__init__(self, engine_config)
        threading.Thread.__init__(self, **kwargs)
        self._driver_cls = load_class(engine_config.driver_cls, Driver)
        self._component_factory = component_factory
        self._runtime_context = runtime_context
        self._stop_trigger = stop_trigger
        self._start_trigger = start_trigger
        self._logger = logging.getLogger(self.name)

    def run(self):
        driver = None
        try:
            self._start_trigger.set()
            self._logger.debug('Start')
            driver = self._driver_cls(
                self.config,
                self._runtime_context,
                self,
                self._component_factory)
            driver.setup()
            driver.run()
        except Exception as e:
            self._logger.error('Unexpected exception, %s' % str(e))
        finally:
            try:
                if driver and hasattr(driver, 'cleanup'):
                    driver.cleanup()
            except Exception as e:
                self._logger.error('Unexpected exception, %s' % str(e))
        self._stop_trigger.set()
        self._logger.debug('Stop')

    def stopping(self):
        return self._stop_trigger.is_set()


class OthreadManager(Configurable):
    def __init__(self, engine_config, runtime_context, component_factory):
        super(OthreadManager, self).__init__(engine_config)
        start_trigger = threading.Event()
        stop_trigger = threading.Event()
        self._start_trigger = start_trigger
        self._stop_trigger = stop_trigger
        thread_cls = load_class(engine_config.thread_cls, Othread)
        self._threads = [thread_cls(
            engine_config, runtime_context, component_factory,
            start_trigger, stop_trigger,
            name='%s-%d' % (thread_cls.__name__, i))
            for i in range(0, engine_config.thread_num)]

    @property
    def thread_num(self):
        return len(self._threads)

    def start(self):
        list(map(lambda t: t.start(), self._threads))
        while not self._start_trigger.wait(0.1):
            if self._start_trigger.is_set():
                break
            

    def setDaemon(self, daemonic):
        list(map(lambda t: t.setDaemon(daemonic), self._threads))

    def join(self):
        list(map(lambda t: t.join(), self._threads))

    def stop(self):
        self._stop_trigger.set()

    def stopped(self):
        return not any([t.isAlive() for t in self._threads])
