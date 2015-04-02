#!/bin/bash

while true; do
    if [ ! -d /Volumes/Frogpond/snaps ]; then
        echo "frogpond not mounted, waiting..."
        sleep 60
        continue
    fi
    echo "sync from pi"
    rsync -av --bwlimit=1500 --progress --exclude '*jpg~' pi@frogpond2.local:snaps/ /Volumes/Frogpond/snaps/ &&
    echo "cleanup pi" &&
    (for d in /Volumes/Frogpond/snaps/2???-??-??; do
        cd "$d"
        dn=`basename "$d"`
        for f in *.jpg; do
           echo "$dn/$f"
        done
    done) | ssh pi@frogpond2.local '~/code/frogpond.io/scripts/remove-files.sh'
    echo "sleeping"
    sleep 120
done
