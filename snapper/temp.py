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

def render(config, output_file):
    output_config = config['output']
    from pylab import rcParams
    rcParams['figure.figsize'] = output_config['width'], output_config['height']

    days = DayLocator()
    dayFmt = DateFormatter('%d/%m')
    #hours = HourLocator()   # every year
    #hoursFmt = DateFormatter('%H:%M')

    fig, ax = plt.subplots()

    def movingaverage(interval, window_size):
        window = numpy.ones(int(window_size))/float(window_size)
        return numpy.convolve(interval, window, 'same')

    for probe in config['probes']:
        probe_config = config['probes'][probe]
        label = probe_config['label']
        dates = []
        temps = []
        with open(os.path.expanduser(probe)) as fd:
            r = csv.reader(fd)
            for row in r:
                if len(row) == 2:
                    try:
                        dates.append(datetime.datetime.fromtimestamp(float(row[0])))
                        temps.append(float(row[1]))
                    except:
                        print(row)
                        raise
        n = output_config['smoothing']
        assert(n % 2 == 1)
        assert(n > 0)
        ax.plot_date(dates[n/2:-n/2], movingaverage(temps, n)[n/2:-n/2], '-', label=label)

    # format the ticks
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(dayFmt)
    #ax.xaxis.set_minor_locator(minutes)
    ax.autoscale_view()

    ax.fmt_xdata = DateFormatter('%H:%M')
    ax.grid(True)
    fig.autofmt_xdate()
    plt.legend()
    plt.savefig(output_file, bbox_inches='tight')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    parser.add_argument('output_file')
    args = parser.parse_args()
    with open(args.config_file) as fd:
        config = yaml.load(fd)
    render(config, args.output_file)

