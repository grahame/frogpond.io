import datetime
import time
import os
from subprocess import call
from astral import Astral

def safe_mkdir(d):
    try:
        os.mkdir(d)
    except OSError:
        pass


class Timelapse(object):
    def __init__(self, directory, city_data, interval):
        self.tz = city_data.tz
        self.date = datetime.datetime.now(tz=self.tz)
        self.sun = city_data.sun(self.date, local=True)
        self.directory = os.path.join(
                directory,
                self.date.strftime("%Y-%m-%d"))
        self.interval = interval
        safe_mkdir(self.directory)

    def time_today(self, tm):
        return self.date.year == tm.year and \
                self.date.month == tm.month and \
                self.date.day == tm.day

    def getmode(self, now):
        if now < self.sun['dawn'] or now > self.sun['sunset']:
            return 'night'
        else:
            return 'day'

    def timed_call(self, args):
        now = time.time()
        code = call(args)
        return code, time.time() - now

    def acquire(self):
        while True:
            now = datetime.datetime.now(tz=self.tz)
            if not self.time_today(now):
                return
            timestamp = time.mktime(now.timetuple())
            outf = os.path.join(
                    self.directory,
                    "%d.jpg" % (timestamp))
            args = ['raspistill', '-vf', '-hf', '-o', outf]
            mode = self.getmode(now)
            if mode == 'night':
                args += ['--shutter', '200000', '-awb', 'off', '-awbg', '1,1']
            rv, elapsed = self.timed_call(args)
            print '%s (mode %s, code %d, elapsed %.1fs)' % (outf, mode, rv, elapsed)
            sleep_time = self.interval - elapsed
            if sleep_time > 0:
                time.sleep(10)


def go(city, directory, interval):
    safe_mkdir(directory)
    a = Astral()
    city_data = a[city]
    while True:
        lapse = Timelapse(
                directory,
                city_data,
                interval)
        lapse.acquire()
