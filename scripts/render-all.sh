#!/bin/bash

base=/Volumes/Frogpond/snaps/

dirs() {
    emit=""
    for i in `echo "$base"????-??-??/`; do
        if [ x"$emit" != x ]; then
            echo $emit
        fi
        emit="$i"
    done
}

for i in $( dirs ); do
    b="`basename $i`"
    movie=$base"daily/$b".mp4
    if [ ! -f "$movie" ]; then
        ./render.sh "$i" 24 "$movie"
    fi
done