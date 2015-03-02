#!/usr/bin/env python

import argparse
from .snap import go

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('city')
    parser.add_argument('directory')
    args = parser.parse_args()
    go(args.city, args.directory)

