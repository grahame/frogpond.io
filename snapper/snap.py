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
    def __init__(self, date, directory):
        self.date = date
        self.directory = directory
        safe_mkdir(directory)

    def time_today(self, tm):
        return self.date.year == tm.year and \
                self.date.month == tm.month and \
                self.date.day == tm.day

    def acquire(self):
        while True:
            now = datetime.datetime.now()
            mode = 'day'
            if not self.time_today(now):
                return
            timestamp = time.mktime(now.timetuple())
            outf = os.path.join(
                    self.directory,
                    "%d.jpg" % (timestamp))
            args = ['raspistill', '-vf', '-hf', '-o', outf]
            rv = call(args)
            print 'took a photo in %s mode -> %s (%d)' % (mode, outf, rv)
            time.sleep(10)


def go(city, directory):
    safe_mkdir(directory)
    while True:
        today = datetime.date.today()
        lapse = Timelapse(
                today,
                os.path.join(directory, today.strftime("%Y-%m-%d")))
        lapse.acquire()
