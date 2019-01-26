#!/home/pi/empty/bin/python
import time, sys
from operator import itemgetter

import gnc

gnc = gnc.GNC()
gnc.lsm303_sampling(.01)

observations = []
mxpeaks = []
mypeaks = []
while True:
    time.sleep(.1)
    now,ax,ay,az,rmx,rmy,rmz,mx,my,mz,heading = gnc.getlsm303()
    if ax == None:
        continue
    obs = (now,ax,ay,az,mx,my,mz,heading)
    disp = '%-12s'%('      '+'*'*int(round(abs(heading)/30.0,0)),)
    if heading < 0:
        disp = disp[::-1]
    print ("%8.3f %+5.0f %+5.0f %+5.0f %+9.3f %+9.3f %+9.3f %+8.3f"%obs + " " + disp)
