#!/usr/bin/env python3

from glob import glob
from PIL import Image
from hashlib import sha1
import hashlib
import subprocess
import datetime
import argparse
import time
import sys
import os


class Library:
    @classmethod
    def days(cls, base='/Volumes/Frogpond*'):
        days = glob(base+'/snaps/*/')
        yield from sorted(days, key=lambda x: x.split('/')[-2])

    @classmethod
    def images(cls, path):
        for fname in glob(os.path.join(path, '*.jpg')):
            yield fname

    @classmethod
    def qcpath(cls, path):
        return os.path.join(path, 'qc_ok.txt')

    @classmethod
    def qcok(cls, path):
        return os.access(Library.qcpath(path), os.R_OK)

    @classmethod
    def quarantine(cls, fname):
        parts = fname.split('/')
        assert(parts[1] == 'Volumes')
        volume = '/'.join(parts[:3])
        qdir = os.path.join(volume, 'quarantine')
        target = os.path.join(qdir, os.path.basename(fname))
        print("quarantine: `%s' -> `%s'" % (fname, target))
        os.rename(fname, target)


def command_qc(args):
    # 1425513431.jpg 2592 x 1944 24bit Exif  N 3358723  Corrupt JPEG data: 32765 extraneous bytes before marker 0xd9  [WARNING]
    # 1425513446.jpg 2592 x 1944 24bit Exif  N 3340226  [OK]
    # 1425513461.jpg 2592 x 1944 24bit Exif  N 3342530  [OK]
    for day_path in Library.days(base=args.base):
        print()
        print(day_path)
        if Library.qcok(day_path):
            print("done, skipping")
            continue
        os.chdir(day_path)
        files = glob('*.jpg')
        print('%d files to check.' % len(files))
        with subprocess.Popen(["jpeginfo", "-c"] + files, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as proc:
            for line in (t.strip() for t in proc.stdout):
                sys.stderr.write('.')
                sys.stderr.flush()
                parts = line.split()
                if parts[-1] != '[OK]':
                    print(line)
                    quarantine(os.path.join(day_path, parts[0]))

def command_timelapse(args):
    arg_hash = sha1(bytes(repr(args), 'utf8')).hexdigest()
    tmpdir = './tmp-%s' % (arg_hash)
    os.mkdir(tmpdir)
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    photos = []
    photo_dir = {}
    for day_path in Library.days():
        print("scan: %s" % day_path)
        try:
            day = datetime.datetime.strptime(day_path.split('/')[-2], "%Y-%m-%d")
        except ValueError:
            continue
        if day < start_date:
            continue
        if day > end_date:
            continue
        for fname in Library.images(day_path):
            tm = int(os.path.basename(fname).split('.')[0])
            photos.append(tm)
            photo_dir[tm] = day_path
    earliest = photos[0]
    latest = photos[-1]
    frames = args.fps * args.duration
    time_per_frame = (latest - earliest) / (frames - 1)
    idx = 0
    to_render = []
    for frame in range(frames):
        target = earliest + time_per_frame * frame
        while True:
            dist = abs(target - photos[idx])
            options = list(range(max(idx-1,0), min(idx+2, len(photos))))
            distances = [abs(target - photos[t]) for t in options]
            closest = min(distances)
            opt = distances.index(closest)
            next_idx = options[opt]
            #print(idx, dist, options, distances, opt)
            if next_idx == idx:
                break
            idx = next_idx
        print(target, idx)
        photo = photos[idx]
        to_render.append(os.path.join(photo_dir[photo], '%d.jpg' % photo))
    assert(len(to_render) == frames)
    for idx, frame in enumerate(to_render):
        os.symlink(frame, os.path.join(tmpdir, '%d.jpg' % idx))
    subprocess.call([
        'ffmpeg', '-f', 'image2', '-r', str(args.fps),
        '-i', tmpdir+'/%d.jpg', '-r', str(args.fps),
        '-vcodec', 'libx264', 'render-%s.mp4' % arg_hash])
    #subprocess.call(['rm', '-rf', tmpdir])

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_qc = subparsers.add_parser('qc')
    parser_qc.set_defaults(func=command_qc)
    parser_qc.add_argument('base', type=str)

    parser_timelapse = subparsers.add_parser('timelapse')
    parser_timelapse.set_defaults(func=command_timelapse)
    parser_timelapse.add_argument('start_date', type=str)
    parser_timelapse.add_argument('end_date', type=str)
    parser_timelapse.add_argument('duration', type=int)
    parser_timelapse.add_argument('fps', type=int)

    args = parser.parse_args()
    func = getattr(args, 'func', command_qc)
    func(args)

if __name__ == '__main__':
    main()
