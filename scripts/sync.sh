#!/bin/bash

base="/Volumes/Frogpond/snaps"
host="frogpond2.local"

while true; do
    if [ ! -d "$base" ]; then
        echo "frogpond not mounted, waiting..."
        sleep 60
        continue
    fi
    echo "bundling photos on pi" &&
    ssh pi@"$host" "~/code/frogpond.io/scripts/bundle.sh" &&
    echo "grabbing bundles" &&
    rsync -av --progress pi@"$host":snaps/bundles/ "$base"/bundles/ &&
    echo "extract" &&
    (cd "$base" &&
     for i in ./bundles/*.tar; do
         tar xvf "$i" && rm "$i"
     done) &&
    echo "cleanup" &&
    ssh pi@frogpond2.local "rm ~/snaps/bundles/*.tar"
    echo "sleep"
    sleep 10
done
