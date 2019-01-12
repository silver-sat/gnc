#!/usr/bin/env python
import time, sys
import RPi.GPIO as io 
io.setmode(io.BCM) 

if len(sys.argv) < 2:
    print >>sys.stderr, "power.py <pin> [ <pin> ... ]"
    sys.exit(1)
 
io.setwarnings(False)

for pin in sys.argv[1:]:
    try:
        pin = int(pin)
    except ValueError:
	continue
    if abs(pin) not in (4,17,18,22,23,24,25):
	continue
    if pin > 0:
        io.setup(pin, io.OUT)
        io.output(pin, True)
    else:
        io.setup(-pin, io.OUT)
        io.output(-pin, False)

# time.sleep(5)
# io.cleanup()
