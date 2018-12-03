from .common import Queue
from .driver import Driver
from .othread import Othread


class BackendDriver(Driver):
    def __init__(self, config, current_thread):
        super(BackendDriver, self).__init__(config, current_thread)
        self._transport_exists = False
        if hasattr(self.runtime_context, 'transport_thread'):
            self._transport_exists = True
            self._queue = self.runtime_context.backend_thread_queue
        else:
            self._queue = self.runtime_context.frontend_thread_queue

        self._processor = config.engine.backend.processor_cls(config)

    @property
    def queue(self):
        return self._queue

    def run(self):
        while True:
            if self.current_thread.stopping():
                if self.queue.qsize() <= 0:
                    if not self._transport_exists:
                        break
                    elif self.runtime_context.transport_thread.stopped():
                        break

            try:
                data = self.queue.get(block=True, timeout=0.1)
                self._processor.process(data)
            except Queue.Empty:
                pass


class BackendThread(Othread):

    def run(self):
        super(BackendThread, self).run()
        self.runtime_context.frontend_thread.stop()
        if hasattr(self.runtime_context, 'transport_thread'):
            self.runtime_context.transport_thread.stop()

