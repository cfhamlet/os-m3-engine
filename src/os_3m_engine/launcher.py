from os_config import Config

from .common import ConfigurableFactory, Queue
from .core.engine import Engine, RuntimeContext
from .core.othread import OthreadManager
from .utils import load_class

FRONTEND_ENGINE_CONFIG = Config.create(
    thread_cls='os_3m_engine.core.frontend.FrontendThread',
    thread_num=1,
    driver_cls='os_3m_engine.core.frontend.FrontendDriver',
    component_factory_cls='os_3m_engine.common.ComponentFactory',
    queue_size=100,
)
TRANSPORT_ENGINE_CONFIG = Config.create(
    thread_cls='os_3m_engine.core.transport.TransportThread',
    thread_num=3,
    driver_cls='os_3m_engine.core.transport.TransportDriver',
    component_factory_cls='os_3m_engine.common.ComponentFactory',
)

TRANSPORT_BRIDGE_ENGINE_CONFIG = Config.create()
TRANSPORT_BRIDGE_ENGINE_CONFIG.update(TRANSPORT_ENGINE_CONFIG)
TRANSPORT_BRIDGE_ENGINE_CONFIG.driver_cls = 'os_3m_engine.core.transport.BridgeDriver'

BACKEND_ENGINE_CONFIG = Config.create(
    thread_cls='os_3m_engine.core.backend.BackendThread',
    thread_num=1,
    driver_cls='os_3m_engine.core.backend.BackendDriver',
    component_factory_cls='os_3m_engine.common.ComponentFactory',
    queue_size=100,
)

ENGINE_CONFIG = Config.create(
    main_loop_wait=0.1
)


def combine_from_default_config(default_config, custom_config):
    c = Config.create()
    c.update(default_config)
    if custom_config is not None:
        for k, _ in default_config:
            if hasattr(custom_config, k):
                setattr(c, k, getattr(custom_config, k))
    return c


def create(frontend_cls='os_3m_engine.ootb.StdinFrontend',
           transport_cls='os_3m_engine.ootb.LogTransport',
           backend_cls='os_3m_engine.ootb.LogBackend',
           app_config=None,
           engine_config=ENGINE_CONFIG,
           frontend_engine_config=FRONTEND_ENGINE_CONFIG,
           transport_engine_config=TRANSPORT_BRIDGE_ENGINE_CONFIG,
           backend_engine_config=BACKEND_ENGINE_CONFIG,
           runtime_context=None):

    if frontend_cls is None:
        raise ValueError('Not specifiy frontend_cls')

    if transport_cls is None and backend_cls is None:
        raise ValueError('Spiecify at least one of transport_cls/backend_cls')

    runtime_context = runtime_context if runtime_context is not None else RuntimeContext()

    # init frontend
    frontend_engine_config = combine_from_default_config(
        FRONTEND_ENGINE_CONFIG, frontend_engine_config)

    runtime_context.frontend_thread_queue = Queue.Queue(
        frontend_engine_config.queue_size)

    frontend_factory_cls = load_class(
        frontend_engine_config.component_factory_cls, ConfigurableFactory)
    frontend_factory = frontend_factory_cls(app_config, frontend_cls)
    runtime_context.frontend_thread = OthreadManager(
        frontend_engine_config, runtime_context, frontend_factory)
    runtime_context.frontend_thread.setDaemon(True)

    # init transport
    default_transport_engine_config = TRANSPORT_BRIDGE_ENGINE_CONFIG \
        if backend_cls is not None else TRANSPORT_ENGINE_CONFIG

    if transport_engine_config in (TRANSPORT_ENGINE_CONFIG, TRANSPORT_BRIDGE_ENGINE_CONFIG):
        transport_engine_config = None

    transport_engine_config = combine_from_default_config(
        default_transport_engine_config, transport_engine_config)

    backend_engine_config = combine_from_default_config(
        BACKEND_ENGINE_CONFIG, backend_engine_config)

    if transport_cls:
        if backend_cls:
            runtime_context.backend_thread_queue = Queue.Queue(
                backend_engine_config.queue_size)

        transport_factory_cls = load_class(
            transport_engine_config.component_factory_cls, ConfigurableFactory)
        transport_factory = transport_factory_cls(app_config, transport_cls)
        runtime_context.transport_thread = OthreadManager(
            transport_engine_config, runtime_context, transport_factory)

    # init backend
    if backend_cls:
        backend_factory_cls = load_class(
            backend_engine_config.component_factory_cls, ConfigurableFactory)
        backend_factory = backend_factory_cls(app_config, backend_cls)
        runtime_context.backend_thread = OthreadManager(
            backend_engine_config, runtime_context, backend_factory)

    engine_config = combine_from_default_config(ENGINE_CONFIG, engine_config)
    return Engine(engine_config, runtime_context)
