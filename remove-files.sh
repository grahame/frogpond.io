#!/bin/bash

while read FNAME;
do
    f=~/snaps/"$FNAME"
    [ -f "$f" ] && rm -f "$f"
done

