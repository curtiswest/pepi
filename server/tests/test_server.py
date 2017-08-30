import pytest
from PIL import Image

from server.meta_server import MetaImagingServer

class MetaServerContract(object):
    @pytest.fixture(scope="module")
    def concrete_server(self):
        raise NotImplementedError('You must override the @pytest.fixture `concrete_server`')

    def test_concrete_server_type(self, concrete_server):
        assert isinstance(concrete_server, MetaImagingServer)

    def test_ping(self, concrete_server):
        assert concrete_server.ping() == True

    def test_identify(self, concrete_server):
        identifier = concrete_server.identify()
        assert isinstance(identifier, (str, unicode))
        assert len(identifier) > 0

    def test_stream_url(self, concrete_server):
        assert isinstance(concrete_server.stream_url(), (str, unicode))

    def test_capturing_to_jpg(self, concrete_server):
        import time
        from io import BytesIO
        data_code = 'my_data_code'
        concrete_server.start_capture(data_code)
        time.sleep(1)
        jpg = concrete_server.retrieve_still_jpg(data_code)
        assert isinstance(jpg, (str, unicode))
        assert len(jpg) > 0
        image_bytes = BytesIO(jpg)
        image = Image.open(image_bytes)
        assert image.size > (0, 0)
        assert image.format == 'JPEG'

    def test_capturing_to_png(self, concrete_server):
        import time
        from io import BytesIO
        data_code = 'my_data_code'
        concrete_server.start_capture(data_code)
        time.sleep(1)
        png = concrete_server.retrieve_still_png(data_code)
        assert isinstance(png, (str, unicode))
        assert len(png) > 0
        image_bytes = BytesIO(png)
        image = Image.open(image_bytes)
        assert image.size > (0, 0)
        assert image.format == 'PNG'