from ..common import Queue, StandardComponent
from .driver import Driver
from .othread import Othread


class Frontend(StandardComponent):

    def produce(self):
        raise NotImplementedError


class FrontendDriver(Driver):

    @property
    def queue(self):
        return self._runtime_context.frontend_thread_queue

    def run(self):
        for data in self._component.produce():
            while True:
                try:
                    self.queue.put(data, block=False, timeout=1)
                    break
                except Queue.Full:
                    continue
            if self._current_thread.stopping():
                break


class FrontendThread(Othread):

    def run(self):
        super(FrontendThread, self).run()
        if hasattr(self._runtime_context, 'transport_thread'):
            self._runtime_context.transport_thread.stop()
        elif hasattr(self._runtime_context, 'backend_thread'):
            self._runtime_context.backend_thread.stop()
