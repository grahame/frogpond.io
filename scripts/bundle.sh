#!/bin/bash

from="$1"

cd "$from" || exit 1
rmdir ????-??-??/ >/dev/null 2>&1
bundle=$(find ????-??-?? -type f -name "*.jpg" | head -200)
tar cf - $bundle && rm $bundle
