import os
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

    def capture_to_folder(self, fpath, framerate=5, resolution=(640, 480)):
        # type: (str, int, (int,int)) -> None
        """
        Starts a continuous capture of .jpgs to the given `path` at the given `framerate`. For example, this may be used
        in an MJPEG streaming scenario, where new .jpgs are streamed out over the web.
        Args:
            fpath: path to store the images in. Note that write permissions will be needed
            framerate: framerate (fps) to capture at. Recommended range of 1-15fps.
            resolution: the resolution to capture at. Recommended below 720p.
        """

        # noinspection PyShadowingNames
        class CaptureThread(threading.Thread):
            def __init__(self, camera, fpath, framerate, resolution):
                super(CaptureThread, self).__init__()
                self.camera = camera
                self.camera.framerate = framerate
                self.camera.resolution = resolution
                self.out_path = fpath
                self.daemon = True
                self._stopevent = threading.Event()
                if not os.path.exists(fpath):
                    os.makedirs(fpath)

            def run(self):
                for _ in self.camera.capture_continuous(
                                self.out_path + '/img{timestamp:%Y-%m-%d-%H-%M}-{counter:03d}.jpg',
                        use_video_port=True):
                    if self._stopevent.isSet():
                        break

            def stop(self, timeout=None):
                self._stopevent.set()
                threading.Thread.join(self, timeout)
                import shutil
                shutil.rmtree(self.out_path)  # Clean up captures

        self.folder_capture_thread = CaptureThread(camera=self.camera, fpath=fpath, framerate=framerate,
                                                   resolution=resolution)
        self.folder_capture_thread.start()

    def stop_capture_to_folder(self):
        """
        Stops the camera from capturing to the folder, if it was set up in the first place.
        """
        if self.folder_capture_thread:
            self.folder_capture_thread.stop()
