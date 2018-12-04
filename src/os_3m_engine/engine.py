import logging
import signal
import sys
import threading
import time

from .backend import BackendThread, BackendDriver
from .common import Configurable, Queue, RuntimeContext
from .frontend import FrontendThread, FrontendDriver
from .transport import TransportThread, TransportDriver, BridgeDriver
from .utils import getatters, getlastattr
from .othread import OthreadManager


class Engine(Configurable):

    def __init__(self, config, runtime_context):
        super(Engine, self).__init__(config)
        self.__start_lock = threading.Lock()
        self.__started = False
        self.__stopped = False
        self._runtime_context = runtime_context

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


class DEFAULT_FRONTEND_CONFIG(object):
    thread_num = 1
    driver_cls = FrontendDriver


class DEFAULT_TRANSPORT_CONFIG(object):
    thread_num = 10


class DEFAULT_BACKEND_CONFIG(object):
    thread_num = 


def create(frontend_config=DEFAULT_FRONTEND_CONFIG,
           transport_config=DEFAULT_TRANSPORT_CONFIG,
           backend_config=DEFAULT_BACKEND_CONFIG,
           app_config=None, runtime_context=None):

    if frontend_config is None:
        raise ValueError('No frontend config')

    if transport_config is None and backend_config is None:
        raise ValueError('Config at least one of transport/backend')

    runtime_context = runtime_context if runtime_context is not None else RuntimeContext()

    runtime_context.frontend_thread_queue = Queue.Queue(
        engine_config.frontend.queue_size)

    runtime_context.frontend_thread = OthreadManager(
        app_config, runtime_context,
        FrontendThread, engine_config.frontend.thread_num,
        engine_config.frontend.driver_cls)
    runtime_context.frontend_thread.setDaemon(True)

    if hasattr(engine_config, 'transport'):

        if hasattr(engine_config, 'backend'):
            runtime_context.backend_thread_queue = Queue.Queue(
                engine_config.backend.queue_size)

        runtime_context.transport_thread = OthreadManager(
            app_config, runtime_context,
            TransportThread, engine_config.transport.thread_num,
            engine_config.transport.driver_cls)

    if hasattr(engine_config, 'backend'):
        runtime_context.backend_thread = OthreadManager(
            app_config, runtime_context,
            BackendThread, engine_config.backend.thread_num,
            engine_config.backend.driver_cls)

    return Engine(engine_config, runtime_context)
