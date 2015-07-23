#!/bin/bash -x

base="/Volumes/Frogpond/snaps"
host="frogpond"
spleep=10

set -e

grab() {
    echo "grabbing a bundle of photos from pi: $1" &&
    (ssh pi@"$host" "~/code/frogpond.io/scripts/bundle.sh" "$1" | (cd "$base" && tar xvf -) )
}

while true; do
    if [ ! -d "$base" ]; then
        echo "frogpond not mounted, waiting..."
        sleep 60
        continue
    fi
    ssh pi@"$host" df -h "/home/pi/snaps/" "/usb/snaps/"
    grab "/home/pi/snaps/"
    grab "/usb/snaps/"
    rsync -av --progress pi@"$host":"~/snaps/*.csv" "$base"/
    echo "sleep $spleep" &&
    sleep $spleep
done
