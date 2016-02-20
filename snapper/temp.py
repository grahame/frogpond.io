# -*- coding: utf8 -*-

import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, DateFormatter
import itertools
import datetime
import yaml
import numpy
import csv
import sys
import os

class ProbeData(object):
    def __init__(self):
        # cache the temperature readings
        self._cache = {}

    def _read(self, probe_path):
        dates = []
        temps = []
        with open(probe_path) as fd:
            r = csv.reader(fd)
            for row in r:
                if len(row) == 2:
                    try:
                        date = datetime.datetime.fromtimestamp(float(row[0]))
                        temp = float(row[1])
                    except:
                        print(row)
                        continue
                dates.append(date)
                temps.append(temp)
        return dates, temps

    def read(self, probe_path, date_min=None):
        if probe_path not in self._cache:
            self._cache[probe_path] = self._read(probe_path)
        dates, temps = self._cache[probe_path]
        if date_min is None:
            return dates, temps
        d, t = [], []
        for idx, date in enumerate(dates):
            if date < date_min:
                continue
            d.append(date)
            t.append(temps[idx])
        return d, t

def render(data, config):
    output_config = config['output']
    from pylab import rcParams
    rcParams['figure.figsize'] = output_config['width'], output_config['height']

    days = DayLocator()
    dayFmt = DateFormatter('')# %d/%m')
    hours = HourLocator()   # every year
    hoursFmt = DateFormatter('%H:%M')

    fig, ax = plt.subplots()

    def movingaverage(interval, window_size):
        window = numpy.ones(int(window_size))/float(window_size)
        return numpy.convolve(interval, window, 'same')

    date_min = None
    if 'last' in config:
        last_hrs = int(config['last'].get('hours', '0'))
        last_days = int(config['last'].get('days', '0'))
        date_min = datetime.datetime.now() - datetime.timedelta(days=last_days, hours=last_hrs)

    longest_label = max(len(c['label']) for c in config['probes'].values())

    for probe in sorted(config['probes'], key=lambda c: config['probes'][c]['label']):
        probe_config = config['probes'][probe]
        probe_path = os.path.expanduser(probe)
        dates, temps = data.read(probe_path, date_min)

        def agg_time(f):
            f_t = f(temps)
            idx = temps.index(f_t)
            return f_t, dates[idx].strftime('%H:%M:%S')

        min_temp, min_temp_dt = agg_time(min)
        max_temp, max_temp_dt = agg_time(max)
        label = "%*s - min %2.1f$^\circ$ @ %s - max %2.1f$^\circ$ @ %s" % (longest_label, probe_config['label'], min_temp, min_temp_dt, max_temp, max_temp_dt)
        #n = output_config['smoothing']
        #assert(n % 2 == 1)
        #assert(n > 0)
        #lines = ax.plot_date(dates[n/2:-n/2], movingaverage(temps, n)[n/2:-n/2], '-', label=label)
        lines = ax.plot_date(dates, temps, '-', label=label)
        plt.setp(lines, linewidth=3.)

    # format the ticks
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(dayFmt)
    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_minor_formatter(hoursFmt)
    ax.autoscale_view()

    ax.fmt_xdata = DateFormatter('%H:%M')
    ax.xaxis.grid(b=True, which='major', linestyle='-')
    ax.xaxis.grid(b=True, which='minor', linestyle=':')
    ax.yaxis.grid(b=True, which='major', linestyle=':')
    fig.autofmt_xdate()
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.08),
            ncol=1, fancybox=True, shadow=True, prop={'family': 'monospace'})
    plt.savefig(os.path.expanduser(output_config['filename']), bbox_inches='tight')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs='*')
    args = parser.parse_args()
    data = ProbeData()
    for config_file in args.config_file:
        with open(config_file) as fd:
                config = yaml.load(fd)
        render(data, config)

