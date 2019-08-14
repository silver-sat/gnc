 
import threading, time, sys, math

import gps
from Adafruit_LSM303 import LSM303

noio = False
try:
    import RPi.GPIO as io 
except ImportError:
    noio = True

class GNC(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}

        self.gpssleep = 1 # sample GPS every 1 second

        self.start = time.time()

        t = threading.Thread(target=self.poll_gps)
        t.daemon = True
        t.start()

        self.lsm303sleep = 1 # sample chip every 1 second

        t = threading.Thread(target=self.poll_lsm303)
        t.daemon = True
        t.start()

        if not noio:
           io.setmode(io.BCM) 
           io.setwarnings(False)

    def lsm303_sampling(self,value=None):
        if value == None:
            return self.lsm303sleep
        self.lsm303sleep = value

    def get(self,*args):
        try:
            self.lock.acquire()
            return tuple(map(self.data.get,args))
        finally:
            self.lock.release()

    def set(self,**kwargs):
        try:
            self.lock.acquire()
            self.data.update(kwargs)
        finally:
            self.lock.release()

    def ready(self):
        if None in self.get('lat','lon','alt'):
            return False
        if None in self.get('lsm303time','heading'):
            return False
        return True

    def position(self):
        return self.get('gpstime','lat','lon','alt')

    def orientation(self):
        return self.get('lsm303time','calmagx','calmagy','calmagz')

    def heading(self):
        return self.get('lsm303time','heading')

    def acceleration(self):
        return self.get('lsm303time','accelx','accely','accelz')

    def getlsm303(self):
        return self.get('lsm303time','accelx','accely','accelz','rawmagx','rawmagy','rawmagz','calmagx','calmagy','calmagx','heading')

    def poll_lsm303(self):

        # set up LSM303
        lsm303 = LSM303()
        max_mag_x = max_mag_y = max_mag_z = -1e-20
        min_mag_x = min_mag_y = min_mag_z = +1e-20

        while True:
            accel, mag = lsm303.read()
            now = time.time()
            accel_x, accel_y, accel_z = accel
            mag_x, mag_z, mag_y = mag 

            max_mag_x = max(max_mag_x,mag_x)
            min_mag_x = min(min_mag_x,mag_x)
            max_mag_y = max(max_mag_y,mag_y)
            min_mag_y = min(min_mag_y,mag_y)
            max_mag_z = max(max_mag_z,mag_z)
            min_mag_z = min(min_mag_z,mag_z)

            off_mag_x = (max_mag_x + min_mag_x)/2
            off_mag_y = (max_mag_y + min_mag_y)/2
            off_mag_z = (max_mag_z + min_mag_z)/2

            sca_mag_x = 1.0 if (max_mag_x == min_mag_x) else 2000.0/(max_mag_x-min_mag_x)
            sca_mag_y = 1.0 if (max_mag_y == min_mag_y) else 2000.0/(max_mag_y-min_mag_y)
            sca_mag_z = 1.0 if (max_mag_z == min_mag_z) else 2000.0/(max_mag_z-min_mag_z)

            cal_mag_x = sca_mag_x * (mag_x - off_mag_x)
            cal_mag_y = sca_mag_y * (mag_y - off_mag_y)
            cal_mag_z = sca_mag_z * (mag_z - off_mag_z)

            heading2d = math.atan2(cal_mag_y,cal_mag_x)*180.0/math.pi
            
            kw = dict(rawmagx=mag_x,rawmagy=mag_y,rawmagz=mag_z,
                      calmagx=cal_mag_x,calmagy=cal_mag_y,calmagz=cal_mag_z,
                      heading=heading2d,
                      accelx=accel_x,accely=accel_y,
                      accelz=accel_z,
                      lsm303time=(now-self.start))
            self.set(**kw)
            time.sleep(self.lsm303sleep)

    def poll_gps(self):

        # set up GPS
        session = gps.gps("localhost", "2947")
        session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

        while True:
            report = session.next()
            now = time.time()
            kw = {'gpstime': (now-self.start)}
            for key in ('lat','lon','alt'):
                if hasattr(report,key) and getattr(report,key):
                    kw[key] = getattr(report,key)
            self.set(**kw)
            time.sleep(self.gpssleep)

    def pin_on(self,pin):
        assert pin in (4,17,18,22,23,24,25)
        io.setup(pin, io.OUT)
        io.output(pin, True)

    def pin_off(self,pin):
        assert pin in (4,17,18,22,23,24,25)
        io.setup(pin, io.OUT)
        io.output(pin, False)

if __name__ == "__main__":

    gnc = GNC()
    while not gnc.ready():
        print("Waiting for GPS to be ready.")
        time.sleep(5)
        
    while True:
        print ("Position: {0}".format(gnc.position()))
        print ("Orientation: {0}".format(gnc.orientation()))
        print ("Acceleration: {0}".format(gnc.acceleration()))
        time.sleep(5)
