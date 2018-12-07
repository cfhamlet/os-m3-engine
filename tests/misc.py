import time
from os_m3_engine.core.backend import Backend
from os_m3_engine.core.frontend import Frontend
from os_m3_engine.core.transport import Transport

DATA = 'Hello World!'


class SleepFrontend(Frontend):
    def produce(self):
        time.sleep(100)
        yield DATA


class OneRecordFrontend(Frontend):
    def produce(self):
        assert 1 == 1
        yield DATA


class ConfirmTransport(Transport):
    def transport(self, data):
        assert data == DATA
        return data


class ConfirmBackend(Backend):
    def process(self, data):
        assert data == DATA
