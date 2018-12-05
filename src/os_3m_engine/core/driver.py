from ..common import Configurable, Workflowable


class Driver(Configurable, Workflowable):

    def __init__(self, engine_config, runtime_context, current_thread, component_factory):
        super(Driver, self).__init__(engine_config)
        self._runtime_context = runtime_context
        self._current_thread = current_thread
        self._component = component_factory.create(
            engine_config, runtime_context, current_thread)

    def setup(self):
        self._component.setup()

    def cleanup(self):
        self._component.cleanup()

    def run(self):
        raise NotImplementedError
