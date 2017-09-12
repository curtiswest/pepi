import pytest

from .test_camera import MetaCameraContract
from ..dummyimager import DummyCamera


class TestDummyCamera(MetaCameraContract):
    @pytest.fixture(scope="module")
    def camera(self):
        return DummyCamera(resolution=(640, 480))
