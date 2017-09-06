import pytest

from server.tests import MetaServerContract, MetaServerOverThrift
from raspi_server.raspi_server import RaspPiImagingServer
from server.dummyimager import DummyImager


class TestRaspiServer(MetaServerContract):
    @pytest.fixture(scope="module")
    def server(self):
        return RaspPiImagingServer(imagers=[DummyImager(resolution=(4, 3)), DummyImager(resolution=(4, 3))],
                                   stream=False)


class TestRaspiServerOverThrift(MetaServerOverThrift):
    @pytest.fixture(scope="module")
    def local_server(self):
        return RaspPiImagingServer(imagers=[DummyImager(resolution=(4, 3)), DummyImager(resolution=(4, 3))],
                                   stream=False)
