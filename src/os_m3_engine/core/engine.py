import threading
import time

from ..common import Configurable
from ..utils import getatters


class RuntimeContext(object):
    pass


class Engine(Configurable):

    def __init__(self, config, runtime_context):
        super(Engine, self).__init__(config)
        self.__start_lock = threading.Lock()
        self.__started = False
        self.__stopped = False
        self._runtime_context = runtime_context

    def started(self):
        return self.__started

    def stopped(self):
        return self.__stopped

    def start(self):

        self.__acquire_start_lock(False, 'Can not start twice')
        runtime_context = self._runtime_context
        m = getatters(runtime_context, [
                      'backend_thread',
                      'transport_thread',
                      'frontend_thread'
                      ])
        list(map(lambda x: x.start(), m))

        self.__started = True
        self.__start_lock.release()

        while not any([x.stopped() for x in m]):
            time.sleep(self.config.main_loop_wait)

        m = getatters(runtime_context, [
            'transport_thread',
            'backend_thread'
        ])
        list(map(lambda x: x.join(), m))
        self.__stopped = True

    def __acquire_start_lock(self, started, err_msg):
        self.__start_lock.acquire()
        if self.__started != started:
            try:
                raise RuntimeError(err_msg)
            finally:
                self.__start_lock.release()

    def __stop(self):
        runtime_context = self._runtime_context
        runtime_context.frontend_thread.stop()
        if hasattr(runtime_context, 'transport_thread'):
            runtime_context.transport_thread.stop()
        elif hasattr(runtime_context, 'backend_thread'):
            runtime_context.backend_thread.stop()
        self.__stopped = True
        self.__started = False

    def stop(self):
        self.__acquire_start_lock(True, 'Can stop before start')
        if not self.__stopped:
            self.__stop()
        self.__start_lock.release()
