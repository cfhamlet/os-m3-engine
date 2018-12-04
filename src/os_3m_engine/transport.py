from .common import Configurable, Queue
from .driver import Driver
from .othread import Othread


class TransportDriver(Driver):
    def __init__(self, config, current_thread):
        super(TransportDriver, self).__init__(config, current_thread)
        self._processor = self.config.engine.transport.processor_cls(config)
        self._backend_exists = False
        if hasattr(self.runtime_context, 'backend_thread'):
            self._backend_exists = True

    @property
    def input_queue(self):
        return self.runtime_context.frontend_thread_queue

    def _process(self, data):
        self._processor.process(data)

    def run(self):
        while True:
            if self.current_thread.stopping():
                if self.input_queue.qsize() <= 0:
                    break
                elif self._backend_exists:
                    if self.runtime_context.backend_thread.stopped():
                        break

            try:
                data = self.input_queue.get(block=True, timeout=0.1)
                self._process(data)
            except Queue.Empty:
                pass


class BridgeDriver(TransportDriver):

    @property
    def output_queue(self):
        return self.runtime_context.backend_thread_queue

    def _process(self, data):
        p_data = self._processor.process(data)
        while True:
            try:
                self.output_queue.put(p_data, block=True, timeout=0.1)
                break
            except Queue.Full:
                pass


class TransportThread(Othread):

    def run(self):
        super(TransportThread, self).run()
        self.runtime_context.frontend_thread.stop()
        if hasattr(self.runtime_context, 'backend_thread'):
            self.runtime_context.backend_thread.stop()


class Transport(Configurable):
    def transport(self):
        raise NotImplementedError
