from ..common import Queue, StandardComponent
from .driver import Driver
from .othread import Othread


class Backend(StandardComponent):
    def process(self, data):
        raise NotImplementedError


class BackendDriver(Driver):

    def setup(self):
        if hasattr(self._runtime_context, 'transport_thread'):
            self._queue = self._runtime_context.backend_thread_queue
        else:
            self._queue = self._runtime_context.frontend_thread_queue
        super(BackendDriver, self).setup()

    @property
    def queue(self):
        return self._queue

    def run(self):
        while True:
            if self._current_thread.stopping():
                if self.queue.qsize() <= 0:
                    if not hasattr(self._runtime_context, 'transport_thread'):
                        break
                    elif self._runtime_context.transport_thread.stopped():
                        break

            try:
                data = self.queue.get(block=True, timeout=0.1)
                self._component.process(data)
            except Queue.Empty:
                pass


class BackendThread(Othread):

    def run(self):
        super(BackendThread, self).run()
        self._runtime_context.frontend_thread.stop()
        if hasattr(self._runtime_context, 'transport_thread'):
            self._runtime_context.transport_thread.stop()
