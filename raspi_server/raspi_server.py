#!/usr/bin/env python

from __future__ import print_function

import logging
import sys
import uuid
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

    def identify(self):
        # type: () -> str
        """
        Get the unique identifier of this server based on the CPU
        serial number.

        :return: the server's unique identifier string
        """
        logging.info('identify()')
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        return line[10:26]
                return super(BaseCameraServer, self).identify()
                return uuid.uuid4().hex[0:16]
        except IOError:
            return uuid.uuid4().hex[0:16]
