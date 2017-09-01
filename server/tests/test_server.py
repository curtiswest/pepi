import imghdr

import pytest
from PIL import Image


# noinspection PyMethodMayBeStatic
class MetaServerContract(object):
    @pytest.fixture(scope="module")
    def concrete_server(self):
        raise NotImplementedError('You must override the @pytest.fixture `concrete_server`')

    def test_ping(self, concrete_server):
        assert concrete_server.ping() is True

    def test_identify(self, concrete_server):
        identifier = concrete_server.identify()
        assert isinstance(identifier, str)
        assert len(identifier) > 0

    def test_stream_url(self, concrete_server):
        assert isinstance(concrete_server.stream_url(), str)

    def test_capturing_to_jpg(self, concrete_server):
        import time
        from io import BytesIO
        data_code = 'my_data_code'
        concrete_server.start_capture(data_code)
        time.sleep(1)
        jpg = concrete_server.retrieve_still_jpg(data_code)

        assert isinstance(jpg, (str, bytes))
        assert len(jpg) > 0
        image_bytes = BytesIO(jpg)
        assert imghdr.what(image_bytes) == 'jpeg'
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
        assert isinstance(png, (str, bytes))
        assert len(png) > 0
        image_bytes = BytesIO(png)
        assert imghdr.what(image_bytes) == 'png'
        image = Image.open(image_bytes)
        assert image.size > (0, 0)
        assert image.format == 'PNG'

    def test_enumerate_methods(self, concrete_server):
        result = concrete_server.enumerate_methods()
        assert isinstance(result, dict)
        assert all([isinstance(key, str) for key in result])
        assert result['ping'] == []
        assert result['identify'] == []
        assert result['stream_url'] == []
        assert result['shutdown'] == []
        assert 'start_capture' in result
        assert 'retrieve_still_jpg' in result
        assert 'retrieve_still_png' in result
        assert 'enumerate_methods' in result
