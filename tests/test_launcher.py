import pytest

from os_m3_engine.core.engine import RuntimeContext
from os_m3_engine.launcher import create


@pytest.fixture(scope='function')
def config():
    from os_config import Config
    return Config.create()


def test_create_001():
    runtime_context = RuntimeContext()
    _ = create(runtime_context=runtime_context)
    for attr in ['frontend_thread_queue', 'backend_thread_queue',
                 'frontend_thread', 'backend_thread', 'transport_thread']:
        assert hasattr(runtime_context, attr)


def test_create_002():
    with pytest.raises(ValueError):
        create(frontend_cls=None)
    with pytest.raises(ValueError):
        create(transport_cls=None, backend_cls=None)


def test_create_003(config):
    config.queue_size = 1000
    config.thread_num = 10
    runtime_context = RuntimeContext()
    _ = create(engine_frontend_config=config,
               engine_backend_config=config,
               runtime_context=runtime_context)
    assert runtime_context.frontend_thread_queue.maxsize == config.queue_size
    assert runtime_context.frontend_thread.thread_num == config.thread_num
    assert runtime_context.backend_thread_queue.maxsize == config.queue_size
    assert runtime_context.backend_thread.thread_num == config.thread_num


def test_create_004(config):
    with pytest.raises(ImportError):
        create('not_exist.What')


def test_create_005(config):
    runtime_context = RuntimeContext()
    _ = create(transport_cls=None, runtime_context=runtime_context)
    for attr in ['thransport_thread', 'backend_thread_queue']:
        assert not hasattr(runtime_context, attr)

    runtime_context = RuntimeContext()
    _ = create(backend_cls=None, runtime_context=runtime_context)
    for attr in ['backend_thread', 'backend_thread_queue']:
        assert not hasattr(runtime_context, attr)


def test_create_006(config):
    runtime_context = RuntimeContext()
    config.thread_num = 10
    _ = create(engine_frontend_config=config, runtime_context=runtime_context)
    assert runtime_context.frontend_thread_queue.maxsize > 10


def test_create_007(config):
    runtime_context = RuntimeContext()
    config.queue_size = 10
    _ = create(engine_frontend_config=config, runtime_context=runtime_context)
    assert runtime_context.frontend_thread_queue.maxsize == 10


def test_create_008(config):
    runtime_context = RuntimeContext()
    config.thread_num = 10
    _ = create(engine_backend_config=config, runtime_context=runtime_context)
    assert runtime_context.backend_thread_queue.maxsize > 10


def test_create_009(config):
    runtime_context = RuntimeContext()
    config.thread_num = 10
    _ = create(transport_cls=None, engine_backend_config=config,
               runtime_context=runtime_context)
    assert runtime_context.frontend_thread_queue.maxsize > 10


def test_create_010(config):
    runtime_context = RuntimeContext()
    config.thread_num = 10
    _ = create(backend_cls=None, engine_transport_config=config,
               runtime_context=runtime_context)
    assert runtime_context.frontend_thread_queue.maxsize > 10
