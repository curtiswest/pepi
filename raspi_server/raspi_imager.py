import threading

from picamera import PiCamera
from picamera.array import PiRGBArray

from server import MetaImager


class RPiCameraImager(MetaImager):
    """
    RaspPiCameraModule is an imager that uses the Raspberry Pi Camera Module v1 to obtain imagery. It is capable of
    taking pictures in various resolutions, but defaults to the maximum resolution of 2592x1944.
    """

    RESOLUTION_MAX = (2592, 1944)

    def __init__(self, resolution=RESOLUTION_MAX):
        # type: ((int, int)) -> None
        super(RPiCameraImager, self).__init__()
        self.camera = PiCamera()
        self.req_reso = resolution
        self.camera.start_preview()
        self.lock = threading.Lock()
        self.folder_capture_thread = None

    def still(self):
        # type: () -> [[(int, int, int)]]
        """
        Captures a still with the cameras current setup.
        """
        with self.lock:
            # Lock is necessary on the camera because this method can be called from different threads with
            # reference to this Imager, but the camera is not thread-safe.
            with PiRGBArray(self.camera) as raw_capture:
                # Save the settings of the camera
                old_resolution = self.camera.resolution
                self.camera.resolution = self.req_reso
                self.camera.capture(raw_capture, format='rgb', use_video_port=False)

                # Restore old camera settings
                self.camera.resolution = old_resolution
                return raw_capture.array[0:self.req_reso[0]][0:self.req_reso[1]]  # Crop to size as can camera rounds up

    def stream_jpg_to_folder(self, path_, max_framerate=3, resolution=(640, 480)):
        def _capture_continuous():
            for _ in self.camera.capture_continuous(path_ + '/img{timestamp:%Y-%m-%d-%H-%M}-{counter:03d}.jpg',
                                                    use_video_port=True):
                pass

        self.camera.framerate = max_framerate
        self.camera.resolution = resolution
        self._streaming_thread = threading.Thread(target=_capture_continuous)
        self._streaming_thread.daemon = True
        self._streaming_thread.start()
