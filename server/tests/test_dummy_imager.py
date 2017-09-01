import pytest

from .test_imager import MetaImagerContract
from ..dummyimager import DummyImager


class TestDummyImager(MetaImagerContract):
    @pytest.fixture(scope="module")
    def concrete_imager(self):
        return DummyImager(resolution=(640, 480))
