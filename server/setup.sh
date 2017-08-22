#!/usr/bin/env bash

#Install Python requirements
pip install -r requirements.txt

# Build mjpg-streamer
sudo apt-get update
sudo apt-get -y install git cmake libjpeg8-dev
git clone https://github.com/jacksonliam/mjpg-streamer.git
cd mjpg-streamer/mjpg-streamer-experimental
make
sudo make install
cd ../.. ; rm -rf mjpg-streamer