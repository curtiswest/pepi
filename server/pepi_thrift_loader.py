import sys
import os
from glob import glob

import thriftpy

# First, find the `pepi` root folder
tail = 'pepi'
head = os.path.abspath('.')
if not os.path.exists(head + '/' + tail):
    while not os.path.exists(head + '/' + tail):
        if head == '/':
            print('Could not find {} folder'.format(tail))
            sys.exit([1])
        head, _ = os.path.split(head)

print('Got path as : {}'.format(head + '/' + tail))

# Then, walk through the folders to find the path to `pepi.thrift`
pepi_thrift_path = [y for x in os.walk(head + '/' + tail) for y in glob(os.path.join(x[0], 'pepi.thrift'))]

print('Got pepi_thrift_path as : {}'.format(pepi_thrift_path))

pepi_thrift = thriftpy.load(pepi_thrift_path[0], module_name='pepi_thrift')
print(pepi_thrift)
print(pepi_thrift.__dict__)
ImageUnavailable = pepi_thrift.ImageUnavailable
