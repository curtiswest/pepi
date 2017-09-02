#!/usr/bin/env python

if __name__ == "__main__":
    import thriftpy
    from thriftpy.rpc import make_server

    from raspi_server import RaspPiImagingServer
    from raspi_imager import RPiCameraImager

    poc_thrift = thriftpy.load('../poc.thrift', module_name='poc_thrift')
    handler = RaspPiImagingServer(imager=RPiCameraImager())
    server = make_server(poc_thrift.ImagingServer, handler, '0.0.0.0', 6000)
    print('Starting RaspPiImagingServer')
    server.serve()
