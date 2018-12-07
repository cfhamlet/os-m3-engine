import sys

from .utils import load_class

_PY3 = sys.version_info[0] == 3

if _PY3:
    import queue as Queue
    binary_stdin = sys.stdin.buffer
else:
    import Queue
    if sys.platform == "win32":
        # set sys.stdin to binary mode
        import os
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    binary_stdin = sys.stdin


class Configurable(object):
    def __init__(self, config):
        self._config = config

    @property
    def config(self):
        return self._config


class Workflowable(object):
    def setup(self):
        pass

    def cleanup(self):
        pass


class Component(Configurable, Workflowable):
    pass


class StandardComponent(Component):
    def __init__(self, component_config, engine_config, runtime_context, current_thread):
        super(StandardComponent, self).__init__(component_config)
        self._engine_config = engine_config
        self._runtime_context = runtime_context
        self._current_thread = current_thread


class FactoryInterface(object):
    def create(self, *args, **kwargs):
        raise NotImplementedError


class ConfigurableFactory(Configurable):
    def create(self, *args, **kwargs):
        raise NotImplementedError


class ComponentFactory(ConfigurableFactory):

    def __init__(self, config, component_cls_string):
        super(ComponentFactory, self).__init__(config)
        self._component_cls = load_class(
            component_cls_string, StandardComponent)

    def create(self, engine_config, runtime_context, current_thread):
        return self._component_cls(self.config, engine_config,
                                   runtime_context, current_thread)
