#!/home/pi/empty/bin/python

from operator import itemgetter
import time
import gps

# Listen on port 2947 (gpsd) of localhost
session = gps.gps("localhost", "2947")
session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# import matplotlib
# matplotlib.use('Agg')
# from pylab import *

# plot([1,2,3,4],[1,2,3,4])
# savefig('testgps.png')
# sys.exit(1)

track_values = []
index_values = []
lat_values = []
lon_values = []
index = 1
first = True
start = time.time()
while True:
    try:
        report = session.next()
        # print report
        print ("%5.1f"%(time.time()-start),report['class'])
        # for key in ('lat','lon','alt','track','speed','climb'):
        for key in ('lat','lon','alt'):
           if hasattr(report,key):
                val = getattr(report,key)
                try:
                  val = float(val)
                  valstr = "%+7.2f"%(val,)
                except:
                  valstr = val
                print (key,valstr,)
                if key == "track":
                  track_values.append(val)
                  index_values.append(index)
                  track_values.append(val-360)
                  index_values.append(index)
                  index = index + 1
                if key == "lat":
                  lat_values.append(val)
                if key == "lon":
                  lon_values.append(val)
        if hasattr(report,"satellites"):
           sat = map(lambda d: (d.get('PRN'),d.get('used')),getattr(report,'satellites'))
           used = map(itemgetter(0),filter(lambda t: t[1],sat))
           print ("used"," ".join(map(str,sorted(map(int,used)))),)
           unused = map(itemgetter(0),filter(lambda t: not t[1],sat))
           print ("unused"," ".join(map(str,sorted(map(int,unused)))),)
           
        print

    except KeyError:
        pass
    except KeyboardInterrupt:
        quit()
    except StopIteration:
        session = None
        print ("GPSD has terminated")

