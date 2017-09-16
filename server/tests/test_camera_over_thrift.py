import threading
import sys
import time

import pytest
from thriftpy.rpc import make_server, client_context

from . import AbstractCameraContract
from .. import pepi_thrift

if sys.version_info < (3,):
    text_type = (str, unicode)
    binary_type = str
else:
    text_type = str
    binary_type = bytes


# noinspection PyMethodMayBeStatic
class AbstractCameraOverThrift(AbstractCameraContract):
    @pytest.fixture(scope="module")
    def local_camera(self):
        raise NotImplementedError('You must override the @pytest.fixture `local_camera`')

    @pytest.fixture(scope="session")
    def port(self):
        return 6522

    @pytest.fixture(scope="module")
    def run_server(self, local_camera, port):
        server = make_server(pepi_thrift.Camera, local_camera, '127.0.0.1', port)
        t = threading.Thread(target=server.serve)
        t.daemon = True
        t.start()

    # noinspection PyMethodOverriding
    @pytest.fixture(scope="function")
    def camera(self, run_server, port):
        time.sleep(0.2)
        with client_context(pepi_thrift.Camera, '127.0.0.1', port) as c:
            yield c
