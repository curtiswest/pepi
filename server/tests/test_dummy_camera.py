import pytest

from .test_camera import AbstractCameraContract
from .test_camera_over_thrift import AbstractCameraOverThrift
from ..dummy_camera import DummyCamera


class TestDummyCamera(AbstractCameraContract):
    @pytest.fixture(scope="module")
    def camera(self):
        return DummyCamera(resolution=[1280, 720])


class TestDummyCameraOverThrift(AbstractCameraOverThrift):
    @pytest.fixture(scope="module")
    def local_camera(self):
        return DummyCamera(resolution=[1280, 720])
