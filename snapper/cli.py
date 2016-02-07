#!/usr/bin/env python

import argparse
from .snap import go

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('city')
    parser.add_argument('temp_names')
    parser.add_argument('interval', type=int)
    parser.add_argument('directory', nargs='*')
    args = parser.parse_args()
    print(args.directory)
    temp_names = dict([t.split('=', 1) for t in args.temp_names.split(';')])
    go(args.city, args.directory, args.interval, temp_names)

