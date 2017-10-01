#!/usr/bin/env python

from __future__ import print_function

import sys
# noinspection PyPep8
sys.path.append('../')
sys.path.append('../../')
from server import BaseCameraServer

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '3.0'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class RaspPiCameraServer(BaseCameraServer):
    """
    An implementation of a BaseCameraServer for a Raspberry Pi.
    """
    def __init__(self, cameras, stream=True):
        super(RaspPiCameraServer, self).__init__(cameras, stream)

        # Set identifier based on the RPi's CPU serial number
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        self.identifier = line[10:26]
        except IOError:
            pass