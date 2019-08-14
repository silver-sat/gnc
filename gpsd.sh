#!/bin/sh
set -x
date
sudo killall gpsd
# sudo gpsd /dev/ttyAMA0 -F /var/run/gpsd.sock
sudo gpsd /dev/serial0 -F /var/run/gpsd.sock
# sudo gpsd /dev/ttyS0 -F /var/run/gpsd.sock
# cgps -s
# python3 ./testgps.py
