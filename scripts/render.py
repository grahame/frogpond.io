#!/usr/bin/env python3

import itertools
import subprocess
import glob
import sys
import os

if __name__ == '__main__':
    rate = int(sys.argv[1])
    skip = int(sys.argv[2])
    tmpdir = 'tmprenderpy%d' % os.getpid()
    os.mkdir(tmpdir)

    def files():
        for dirname in sys.argv[2:]:
            for filename in glob.glob(dirname + '/*.jpg'):
                if os.stat(filename).st_size == 0:
                    continue
                yield filename
    try:
        for idx, fname in enumerate(itertools.islice(sorted(files()), 0, None, skip)):
            print(fname)
            os.symlink(fname, os.path.join(tmpdir, '%d.jpg' % idx))
        subprocess.call([
            'ffmpeg', '-f', 'image2', '-r', str(rate),
            '-i', tmpdir+'/%d.jpg', '-r', str(rate),
            '-vcodec', 'libx264', 'out.mp4'])
    finally:
        subprocess.call(['rm', '-rf', tmpdir])


