#!/bin/bash

cd ~/snaps/
rmdir ????-??-??/ >/dev/null 2>&1
bundle=$(find ????-??-?? -type f -name "*.jpg")
out=bundles/"$$.$RANDOM.tar"
tar cf "$out".tmp $bundle && mv "$out".tmp "$out" && rm $bundle
