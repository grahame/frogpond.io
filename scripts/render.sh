#!/bin/bash

working="/Volumes/Frogpond/tmp$$"
mkdir "$working" || exit 1

echo "linking in images: $working"
i=1
for file in `echo "$1"/*jpg | sort`; do
    ln -s "$file" "$working/$i.jpg"
    i=$((i + 1))
done

echo "rendering with ffpmeg, frame rate $2"
ffmpeg -f image2 -r "$2" -i "$working/%d.jpg" -r "$2" -vcodec libx264 "$3"

rm -rf "$working"


