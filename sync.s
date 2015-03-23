#!/bin/bash

while true; do
    echo "sync from pi"
    rsync -av --partial --progress --exclude '*jpg~' pi@frogpond2.local:snaps/ ~/snaps/ &&
    echo "cleanup pi" &&
    (for d in ~/snaps/2???-??-??; do
        cd "$d"
        dn=`basename "$d"`
        for f in *.jpg; do
           echo "$dn/$f"
        done
    done) | ssh pi@frogpond2.local '~/code/frogpond.io/remove-files.sh'
    if [ -d /Volumes/Frogpond/snaps/ ]; then
        echo "sync to external disk"
        rsync -av ~/snaps/ /Volumes/Frogpond/snaps/ &&
            find ~/snaps/2???-??-?? -type f -name "*.jpg" | xargs -n 200 rm -f
    fi
    echo "sleeping"
    sleep 120
done
