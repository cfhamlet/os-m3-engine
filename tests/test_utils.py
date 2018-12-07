import pytest


def test_getatters():
    from os_m3_engine.utils import getatters

    class T(object):
        pass
    t = T()
    t.a = 1
    assert [1] == getatters(t, ['a'])


def test_load_class():
    from os_m3_engine.utils import load_class
    from os_m3_engine.core.engine import Engine
    assert Engine == load_class(
        'os_m3_engine.core.engine.Engine', Engine, True)

    from os_m3_engine.common import Configurable
    from os_m3_engine.common import Component
    assert Component == load_class('os_m3_engine.common.Component')

    assert None == load_class('os_m3_engine.NotExist')

    assert None == load_class('os_m3_engine.common.Component', Engine)

    with pytest.raises(ImportError):
        load_class('not_exist.What')
