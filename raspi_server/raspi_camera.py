"""
raspi_camera.py: Provide a PEPI-compatible Camera backed by a connected Raspberry Pi Camera Module.
"""

import threading
import time
import atexit
import logging
import io

from picamera import *
from picamera.array import PiYUVArray

from server import MetaCamera


class RaspPiCamera(MetaCamera):
    """
    RPiCamera is an camera that uses the Raspberry Pi Camera Module v1/v2 to obtain imagery. It is capable of
    taking pictures in various resolutions, but defaults to the maximum resolution of 2592x1944. It essentially
    serves as a convenient wrapper around PiCamera, but in the PEPI format.
    """

    def __init__(self, resolution=(2592, 1944)):
        # type: ((int, int)) -> None
        super(RaspPiCamera, self).__init__()
        self.camera = PiCamera()
        self.req_reso = resolution
        self.camera.resolution = self.req_reso
        self.camera.start_preview()
        self.lock = threading.RLock()
        self.folder_capture_thread = None

        def cleanup(self):
            logging.info('Closing camera from RPICameraImager..')
            self.camera.close()
            logging.info('Camera closed')

        atexit.register(cleanup, self)

    def still(self):
        # type: () -> [[(int, int, int)]]
        """
        Captures a still with the cameras current setup.
        """
        with self.lock:
            # Lock is necessary on the camera because this method can be called from different threads with
            # reference to this Imager, but the camera is not thread-safe.

            # FIXME: get direct RGB array out of camera (see below note)
            # Below, YUV camera mode is used. This is due to an apparent incompatibility between recording and
            # capturing from the video port at different resolutions, with a resizer thrown in the mix too.
            # The conversion from YUV -> RGB array is very, very slow (~ 5 sec, vs 0.4 sec to capture) and so
            # would ideally be addressed somehow. The best case would be to use the `format='rgb'` parameter
            # when capturing, but testing shows that this results an ENOMEM error - again, something to do with
            # capturing/recording at the same time.
            with PiYUVArray(self.camera) as stream:
                start = time.time()
                self.camera.capture(stream, format='yuv', use_video_port=True)
                logging.debug('Capture took: {}'.format(time.time() - start))
                start = time.time()
                rgb = stream.rgb_array
                logging.debug('RGB conversion took: {}'.format(time.time() - start))
                return rgb[:self.req_reso[0]][:self.req_reso[1]]

    def stream_jpg_to_folder(self, path_, max_framerate=5, resolution=(640, 480)):
        class SplitFrames(object):
            """
            Class based on class from PiCamera's documentation:
            https://picamera.readthedocs.io/en/release-1.13/recipes2.html?#rapid-capture-and-streaming
            """

            def __init__(self, save_path):
                # type: (str) -> None
                self.frame_num = 0
                self.output = None
                self.save_path = save_path

            def write(self, buf):
                """
                Writes to the internal buffer. If a JPG magic number is received, dump to disk in the
                given path.
                :param buf: bytes to write
                :return: None
                """
                if buf.startswith(b'\xff\xd8'):
                    # Start of new frame; close the old one (if any) and open a new output
                    if self.output:
                        self.output.close()
                    self.frame_num += 1
                    self.output = io.open(self.save_path + '/image%02d.jpg' % self.frame_num, 'wb')
                self.output.write(buf)

        if self.camera.recording:
            self.camera.stop_recording()

        output = SplitFrames(save_path=path_)
        self.camera.framerate = max_framerate
        self.camera.resolution = self.req_reso
        self.camera.start_recording(output, 'mjpeg', resize=resolution)
