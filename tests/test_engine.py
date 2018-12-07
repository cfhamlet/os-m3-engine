import threading
import time

import pytest

from os_m3_engine.launcher import create


@pytest.fixture(scope='function')
def config():
    from os_config import Config
    return Config.create()


def test_engine_001(config):

    engine = create(
        frontend_cls='misc.OneRecordFrontend',
        transport_cls='misc.ConfirmTransport',
        backend_cls='misc.ConfirmBackend',
    )
    engine.start()


def test_engine_002(config):
    engine = create(
        frontend_cls='misc.SleepFrontend',
        transport_cls='misc.ConfirmTransport',
        backend_cls='misc.ConfirmBackend',
    )
    t1 = threading.Thread(target=engine.start)
    t1.start()

    while not engine.started():
        time.sleep(0.1)

    engine.stop()
    t1.join()
    assert engine.stopped()


def test_engine_003(config):
    from misc import OneRecordFrontend

    engine = create(
        frontend_cls=OneRecordFrontend,
        transport_cls='misc.ConfirmTransport',
        backend_cls='misc.ConfirmBackend',
    )
    engine.start()
