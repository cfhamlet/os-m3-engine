import logging
import signal
import sys
import threading
import time
from .common import Configurable, RuntimeContext, Queue
from .frontend import FrontendThread
from .transport import TransportThread
from .backend import BackendThread
from .othread import MultithreadManager
from .utils import getatters


class MultithreadEngine(Configurable):

    def __init__(self, config):
        super(MultithreadEngine, self).__init__(config)
        self.__ensure()
        self.__start_lock = threading.Lock()
        self.__started = False
        self.__stopped = False
        self._runtime_context = RuntimeContext()

    def __ensure(self):
        engine_config = self.config.engine
        assert any([hasattr(engine_config, x)
                    for x in ('transport', 'backend')])

    def __setup(self):
        runtime_context = self._runtime_context
        engine_config = self.config.engine

        runtime_context.frontend_thread_queue = Queue.Queue(
            engine_config.frontend.queue_size)

        runtime_context.frontend_thread = MultithreadManager(
            self.config, runtime_context,
            FrontendThread, engine_config.frontend.thread_num,
            engine_config.frontend.driver_cls)
        runtime_context.frontend_thread.setDaemon(True)

        if hasattr(engine_config, 'transport'):

            if hasattr(engine_config, 'backend'):
                runtime_context.backend_thread_queue = Queue.Queue(
                    engine_config.backend.queue_size)

            runtime_context.transport_thread = MultithreadManager(
                self.config, runtime_context,
                TransportThread, engine_config.transport.thread_num,
                engine_config.transport.driver_cls)

        if hasattr(engine_config, 'backend'):
            runtime_context.backend_thread = MultithreadManager(
                self.config, runtime_context,
                BackendThread, engine_config.backend.thread_num,
                engine_config.backend.driver_cls)

    def __start(self):

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
            time.sleep(0.1)

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

    def start(self):
        self.__acquire_start_lock(False, 'Can not start twice')
        self.__setup()
        self.__start()

    def __stop(self):
        runtime_context = self._runtime_context
        runtime_context.frontend_thread.stop()
        if hasattr(runtime_context, 'transport_thread'):
            runtime_context.transport_thread.stop()
        elif hasattr(runtime_context, 'backend_thread'):
            runtime_context.backend_thread.stop()
        self.__stopped = True

    def stop(self):
        self.__acquire_start_lock(True, 'Can stop before start')
        if not self.__stopped:
            self.__stop()
        self.__start_lock.release()
