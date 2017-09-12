import pytest

from server.tests import MetaCameraServerContract, MetaCameraServerOverThrift
from raspi_server.raspi_server import RaspPiCameraServer
from server.dummyimager import DummyCamera


class TestRaspiCameraServer(MetaCameraServerContract):
    @pytest.fixture(scope="module")
    def server(self):
        return RaspPiCameraServer(cameras=[DummyCamera(resolution=(4, 3)), DummyCamera(resolution=(4, 3))],
                                  stream=False)


class TestRaspiServerOverThrift(MetaCameraServerOverThrift):
    @pytest.fixture(scope="module")
    def local_server(self):
        return RaspPiCameraServer(cameras=[DummyCamera(resolution=(4, 3)), DummyCamera(resolution=(4, 3))],
                                  stream=False)
