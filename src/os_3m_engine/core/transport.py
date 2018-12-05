from ..common import Queue, StandardComponent
from .driver import Driver
from .othread import Othread


class Transport(StandardComponent):
    def transport(self, data):
        raise NotImplementedError


class TransportDriver(Driver):

    @property
    def input_queue(self):
        return self._runtime_context.frontend_thread_queue

    def _process(self, data):
        self._component.transport(data)

    def run(self):
        while True:
            if self._current_thread.stopping():
                if self.input_queue.qsize() <= 0:
                    break
                elif hasattr(self._runtime_context, 'backend_thread'):
                    if self._runtime_context.backend_thread.stopped():
                        break

            try:
                data = self.input_queue.get(block=True, timeout=0.1)
                self._process(data)
            except Queue.Empty:
                pass


class BridgeDriver(TransportDriver):

    @property
    def output_queue(self):
        return self._runtime_context.backend_thread_queue

    def _process(self, data):
        p_data = self._component.transport(data)
        while True:
            try:
                self.output_queue.put(p_data, block=True, timeout=0.1)
                break
            except Queue.Full:
                pass


class TransportThread(Othread):

    def run(self):
        super(TransportThread, self).run()
        self._runtime_context.frontend_thread.stop()
        if hasattr(self._runtime_context, 'backend_thread'):
            self._runtime_context.backend_thread.stop()
