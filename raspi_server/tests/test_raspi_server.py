import pytest

from server.tests import MetaServerContract
from raspi_server.raspi_server import RaspPiImagingServer
from server.dummyimager import DummyImager


class TestRaspiServer(MetaServerContract):
    @pytest.fixture(scope="module")
    def concrete_server(self):
        return RaspPiImagingServer(imager=DummyImager())
