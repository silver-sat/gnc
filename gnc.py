
import threading, time, sys, math

import gps
import Adafruit_LSM303
import RPi.GPIO as io 


class GNC(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}

        self.gpssleep = 1 # sample GPS every 1 second

        t = threading.Thread(target=self.poll_gps)
        t.daemon = True
        t.start()

        self.lsm303sleep = 1 # sample chip every 1 second

        t = threading.Thread(target=self.poll_lsm303)
        t.daemon = True
        t.start()

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
        return True

    def position(self):
        return self.get('lat','lon','alt')

    def orientation(self):
        return self.get('magx','magy','magz')

    def heading(self):
        return self.get('heading')[0]

    def acceleration(self):
        return self.get('accelx','accely','accelz')

    def poll_lsm303(self):

        # set up LSM303
        lsm303 = Adafruit_LSM303.LSM303()

        while True:
            accel, mag = lsm303.read()
            accel_x, accel_y, accel_z = accel
            mag_x, mag_z, mag_y = mag 
            heading2d = math.atan2(mag_y,mag_x)*180.0/math.pi
	    
            kw = dict(magx=mag_x,magy=mag_y,magz=mag_z,
		      heading=heading2d,
                      accelx=accel_x,accely=accel_y,
                      accelz=accel_z)
            self.set(**kw)
            time.sleep(self.lsm303sleep)

    def poll_gps(self):

        # set up GPS
        session = gps.gps("localhost", "2947")
        session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

        while True:
            report = session.next()
            kw = {}
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
        print("Waiting for GNC to be ready.")
        time.sleep(5)
        
    while True:
        print ("Position: {0}".format(gnc.position()))
        print ("Orientation: {0}".format(gnc.orientation()))
        print ("Acceleration: {0}".format(gnc.acceleration()))
        time.sleep(5)
