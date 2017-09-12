#!/usr/bin/env python

if __name__ == "__main__":
    import logging

    from thriftpy.rpc import make_server

    from raspi_server import RaspPiCameraServer
    from raspi_camera import RaspPiCamera
    from server import pepi_thrift

    logging.basicConfig(level=logging.DEBUG)
    handler = RaspPiCameraServer(cameras=[RaspPiCamera()], stream=True)
    server = make_server(pepi_thrift.CameraServer, handler, '0.0.0.0', 6000)
    logging.info('Starting RaspPiCameraServer')

    server.daemon = True
    server.serve()
