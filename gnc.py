
import threading, time, sys

import gps
import Adafruit_LSM303

class GNC(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}

        self.gpssleep = 1 # sample GPS every 1 second

        self.t = threading.Thread(target=self.poll_gps)
        self.t.daemon = True
        self.t.start()

        # t = threading.Thread(target=poll_lsm303)
        # t.daemon = True
        # t.start()

    def get(self,*args):
        try:
            self.lock.acquire()
            return map(self.data.get,args)
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

    def acceleration(self):
        return self.get('accelx','accely','accelz')

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

if __name__ == "__main__":

    gnc = GNC()
    while not gnc.ready():
        print("Waiting for GNC to be ready.")
        time.sleep(5)
        
    while True:
        print ("Position: {0}".format(gnc.position()))
        time.sleep(5)
