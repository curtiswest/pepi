#!/bin/bash
echo "Starting PEPI"
python /home/pi/pibox/server.py /home/pi/pibox/id
sleep 30s
/home/pi/pibox/pepi.sh  
