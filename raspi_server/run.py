#!/usr/bin/env python

if __name__ == "__main__":
    import os
    import logging

    import thriftpy
    from thriftpy.rpc import make_server

    from raspi_server import RaspPiImagingServer
    from raspi_imager import RPiCameraImager

    prefix = os.path.abspath('.')
    if not prefix.endswith('pibox'):
        while not prefix.endswith('pibox'):
            prefix, _ = os.path.split(prefix)

    logging.basicConfig(level=logging.DEBUG)

    poc_thrift = thriftpy.load('{}/poc.thrift'.format(prefix), module_name='poc_thrift')
    handler = RaspPiImagingServer(imagers=[RPiCameraImager()], stream=True)
    server = make_server(poc_thrift.ImagingServer, handler, '0.0.0.0', 6000)
    logging.info('Starting RaspPiImagingServer')

    server.daemon = True
    server.serve()

