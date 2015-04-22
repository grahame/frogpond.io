#!/bin/bash

base="/Volumes/Frogpond/snaps"
host="frogpond2.local"
spleep=10

set -e

while true; do
    if [ ! -d "$base" ]; then
        echo "frogpond not mounted, waiting..."
        sleep 60
        continue
    fi
    echo "grabbing a bundle of photos from pi" &&
    (ssh pi@"$host" "~/code/frogpond.io/scripts/bundle.sh" | (cd "$base" && tar xvf -) )
    echo "sleep $spleep" &&
    sleep $spleep
done
