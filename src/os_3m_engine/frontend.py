from .common import Configurable, Queue
from .driver import Driver
from .othread import Othread


class FrontendDriver(Driver):
    def __init__(self, config, current_thread):
        super(FrontendDriver, self).__init__(config, current_thread)
        self._processor = self.config.engine.frontend.processor_cls(config)

    @property
    def queue(self):
        return self.runtime_context.frontend_thread_queue

    def run(self):
        for data in self._processor.process():
            data = data.strip()
            while True:
                if not data:
                    if self.current_thread.stopping():
                        return
                    else:
                        break
                try:
                    self.queue.put(data, block=False, timeout=1)
                    break
                except Queue.Full:
                    continue
            if self.current_thread.stopping():
                break


class FrontendThread(Othread):

    def run(self):
        super(FrontendThread, self).run()
        if hasattr(self.runtime_context, 'transport_thread'):
            self.runtime_context.transport_thread.stop()
        elif hasattr(self.runtime_context, 'backend_thread'):
            self.runtime_context.backend_thread.stop()


class Frontend(Configurable):
    def generate(self):
        raise NotImplementedError
