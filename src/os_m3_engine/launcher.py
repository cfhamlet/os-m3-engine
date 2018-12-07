from os_config import Config

from .common import ConfigurableFactory, Queue
from .core.engine import Engine, RuntimeContext
from .core.othread import OthreadManager
from .utils import load_class

ENGINE_FRONTEND_CONFIG = Config.create(
    thread_cls='os_m3_engine.core.frontend.FrontendThread',
    thread_num=1,
    driver_cls='os_m3_engine.core.frontend.FrontendDriver',
    component_factory_cls='os_m3_engine.common.ComponentFactory',
    queue_size=100,
)

ENGINE_TRANSPORT_CONFIG = Config.create(
    thread_cls='os_m3_engine.core.transport.TransportThread',
    thread_num=3,
    driver_cls='os_m3_engine.core.transport.TransportDriver',
    component_factory_cls='os_m3_engine.common.ComponentFactory',
)

ENGINE_TRANSPORT_BRIDGE_CONFIG = Config.create()
ENGINE_TRANSPORT_BRIDGE_CONFIG.update(ENGINE_TRANSPORT_CONFIG)
ENGINE_TRANSPORT_BRIDGE_CONFIG.driver_cls = 'os_m3_engine.core.transport.BridgeDriver'

ENGINE_BACKEND_CONFIG = Config.create(
    thread_cls='os_m3_engine.core.backend.BackendThread',
    thread_num=1,
    driver_cls='os_m3_engine.core.backend.BackendDriver',
    component_factory_cls='os_m3_engine.common.ComponentFactory',
    queue_size=100,
)

ENGINE_CONFIG = Config.create(
    main_loop_wait=0.1
)


def _queue_size(custorm_config, default_config, thread_num):
    queue_size = custorm_config.queue_size if hasattr(
        custorm_config, 'queue_size') else default_config.queue_size
    if custorm_config == default_config \
            or not hasattr(custorm_config, 'queue_size'):
        queue_size = max(queue_size, thread_num*2)
    return queue_size


def combine_with_default_config(default_config, custom_config):
    c = Config.create()
    c.update(default_config)
    if custom_config is not None:
        for k, _ in default_config:
            if hasattr(custom_config, k):
                setattr(c, k, getattr(custom_config, k))
    return c


def create(frontend_cls='os_m3_engine.ootb.StdinFrontend',
           transport_cls='os_m3_engine.ootb.LogTransport',
           backend_cls='os_m3_engine.ootb.LogBackend',
           app_config=None,
           engine_config=ENGINE_CONFIG,
           engine_frontend_config=ENGINE_FRONTEND_CONFIG,
           engine_transport_config=ENGINE_TRANSPORT_BRIDGE_CONFIG,
           engine_backend_config=ENGINE_BACKEND_CONFIG,
           runtime_context=None):

    if frontend_cls is None:
        raise ValueError('Not specifiy frontend_cls')

    if transport_cls is None and backend_cls is None:
        raise ValueError('Spiecify at least one of transport_cls/backend_cls')

    runtime_context = runtime_context if runtime_context is not None else RuntimeContext()

    # init frontend
    e_frontend_config = combine_with_default_config(
        ENGINE_FRONTEND_CONFIG, engine_frontend_config)

    frontend_factory_cls = load_class(
        e_frontend_config.component_factory_cls, ConfigurableFactory)
    frontend_factory = frontend_factory_cls(app_config, frontend_cls)
    runtime_context.frontend_thread = OthreadManager(
        e_frontend_config, runtime_context, frontend_factory)
    runtime_context.frontend_thread.setDaemon(True)

    # init transport
    default_engine_transport_config = ENGINE_TRANSPORT_BRIDGE_CONFIG \
        if backend_cls is not None else ENGINE_TRANSPORT_CONFIG

    e_transport_config = engine_backend_config
    if engine_transport_config in (ENGINE_TRANSPORT_CONFIG, ENGINE_TRANSPORT_BRIDGE_CONFIG):
        e_transport_config = None

    e_transport_config = combine_with_default_config(
        default_engine_transport_config, e_transport_config)

    e_backend_config = combine_with_default_config(
        ENGINE_BACKEND_CONFIG, engine_backend_config)

    if transport_cls:
        queue_size = _queue_size(
            engine_frontend_config,
            ENGINE_FRONTEND_CONFIG,
            e_transport_config.thread_num)
        e_frontend_config.queue_size = queue_size
        runtime_context.frontend_thread_queue = Queue.Queue(queue_size)

        if backend_cls:
            queue_size = _queue_size(
                engine_backend_config,
                ENGINE_BACKEND_CONFIG,
                e_backend_config.thread_num)
            queue_size = max(queue_size, e_frontend_config.queue_size)
            e_backend_config.queue_size = queue_size
            runtime_context.backend_thread_queue = Queue.Queue(queue_size)

        transport_factory_cls = load_class(
            e_transport_config.component_factory_cls, ConfigurableFactory)
        transport_factory = transport_factory_cls(app_config, transport_cls)
        runtime_context.transport_thread = OthreadManager(
            e_transport_config, runtime_context, transport_factory)
    else:
        queue_size = _queue_size(
            engine_frontend_config,
            ENGINE_FRONTEND_CONFIG,
            e_backend_config.thread_num)

        e_frontend_config.queue_size = queue_size
        e_backend_config.queue_size = queue_size
        runtime_context.frontend_thread_queue = Queue.Queue(queue_size)

        # init backend
    if backend_cls:
        backend_factory_cls = load_class(
            e_backend_config.component_factory_cls, ConfigurableFactory)
        backend_factory = backend_factory_cls(app_config, backend_cls)
        runtime_context.backend_thread = OthreadManager(
            e_backend_config, runtime_context, backend_factory)

    e_config = combine_with_default_config(ENGINE_CONFIG, engine_config)
    return Engine(e_config, runtime_context)
