#!/usr/bin/env python
"""
Launcher for the Raspberry Pi server and camera implementations.
"""

if __name__ == "__main__":
    import logging

    from thriftpy.rpc import make_server

    from raspi_server import RaspPiCameraServer
    from raspi_camera import RaspPiCamera
    from server import pepi_thrift

    logging.basicConfig(level=logging.DEBUG)
    handler = RaspPiCameraServer(cameras=[RaspPiCamera()], stream=True)
    rpi_server = make_server(pepi_thrift.CameraServer, handler, '0.0.0.0', 6000)
    logging.info('Starting RaspPiCameraServer')

    rpi_server.daemon = True
    rpi_server.serve()
