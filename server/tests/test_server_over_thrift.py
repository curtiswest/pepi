import threading
import sys
import time

import pytest
import thriftpy
from thriftpy.rpc import make_server, client_context

from . import MetaServerContract

poc_thrift = thriftpy.load('poc.thrift', module_name='poc_thrift')

if sys.version_info < (3,):
    text_type = (str, unicode)
    binary_type = str
else:
    text_type = str
    binary_type = bytes


# noinspection PyMethodMayBeStatic
class MetaServerOverThrift(MetaServerContract):
    @pytest.fixture(scope="module")
    def local_server(self):
        raise NotImplementedError('You must override the @pytest.fixture `local_server`')

    @pytest.fixture(scope="session")
    def port(self):
        return 6521

    @pytest.fixture(scope="module")
    def run_server(self, local_server, port):
        server = make_server(poc_thrift.ImagingServer, local_server, '127.0.0.1', port)
        t = threading.Thread(target=server.serve)
        t.daemon = True
        t.start()
        return None

    # noinspection PyMethodOverriding
    @pytest.fixture(scope="function")
    def server(self, run_server, port):
        time.sleep(0.2)
        with client_context(poc_thrift.ImagingServer, '127.0.0.1', port) as c:
            yield c
