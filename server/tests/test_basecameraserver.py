import pytest

from .test_server import MetaCameraServerContract
from .test_server_over_thrift import MetaCameraServerOverThrift

from ..base_camera_server import BaseCameraServer
from ..dummy_camera import DummyCamera

class TestBaseCameraServer(MetaCameraServerContract):
    @pytest.fixture(scope="module")
    def server(self):
        return BaseCameraServer([DummyCamera()])