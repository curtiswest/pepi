#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import re
import sys
import subprocess
import os

def check_server(address, port):
    # Create a TCP socket
    s = socket.socket()
    s.settimeout(0.1)
    print "Attempting to connect to %s on port %s" % (address, port)
    try:
        s.connect((address, port))
        print "Connected to %s on port %s" % (address, port)
        s.close()
        return True
    except socket.error, e:
        print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False
    
def sweep_ping(base_address, start=1, stop=255):
    ipList = []
    with open(os.devnull, "wb") as limbo:
        for n in xrange(start, stop):
            ip=base_address+str(n)
            result=subprocess.Popen(["ping", "-c", "1", "-n", "-W", "2", ip],
            stdout=limbo, stderr=limbo).wait()
            if result:
                print ip, "inactive"
            else:
                print ip, "active"
                if check_server(ip, 10000):
                    ipList.append(ip)
                


if __name__ == '__main__':
    port = 10000
    ipList = sweep_ping('192.168.1.')
    if ipList:
        with open("active_cameras.txt", "w") as f:
            [f.write(ip) for ip in ipList]
