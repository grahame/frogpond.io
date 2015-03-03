import datetime
import glob
import time
import csv
import sys
import os
from subprocess import call
from astral import Astral

def safe_mkdir(d):
    try:
        os.mkdir(d)
    except OSError:
        pass

class ThermalLogs(object):
    def __init__(self, directory):
        def outf(f):
            return os.path.join(directory, f.split('/')[-2] + '.csv')
        self.probe_files = dict((outf(t), t) for t in glob.glob('/sys/bus/w1/devices/28-*/w1_slave'))

    def read_dev(self, dev):
        with open(dev) as fd:
            lines = [t.strip() for t in fd.readlines()]
            if len(lines) == 2 and lines[0].endswith(' YES'):
                try:
                    return float(lines[1].split('=')[-1]) / 1000
                except ValueError:
                    return None
            return None

    def update(self):
        vals = []
        for fname, dev in sorted(self.probe_files.items()):
            now, temp = time.time(), self.read_dev(dev)
            vals.append(temp)
            with open(fname, 'a') as fd:
                w = csv.writer(fd)
                w.writerow([now, temp])
        return vals

class Timelapse(object):
    def __init__(self, directory, city_data, interval):
        self.tz = city_data.tz
        self.date = datetime.datetime.now(tz=self.tz)
        self.sun = city_data.sun(self.date, local=True)
        self.thermal = ThermalLogs(directory)
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

    def timed_thermal(self):
        now = time.time()
        vals = self.thermal.update()
        return vals, time.time() - now

    def write_flush(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def acquire(self):
        while True:
            now = datetime.datetime.now(tz=self.tz)
            self.write_flush("acquire: ")
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
            rv, shoot_elapsed = self.timed_call(args)
            vals, thermal_elapsed = self.timed_thermal()
            sleep_time = self.interval - shoot_elapsed - thermal_elapsed
            self.write_flush('%s (%s, %d, s=%.1fs, t=%.1fs, %s). wait %.1fs\n' % (
                os.path.basename(outf), mode, rv, shoot_elapsed, thermal_elapsed, vals, sleep_time))
            if sleep_time > 0:
                time.sleep(sleep_time)


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