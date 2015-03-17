while true; do
    echo "sync from pi"
    rsync -av --partial --progress --exclude '*jpg~' pi@frogpond2.local:snaps/ ~/snaps/
    if [ -d /Volumes/Frogpond/snaps/ ]; then
        echo "sync to external disk"
        rsync -av ~/snaps/ /Volumes/Frogpond/snaps/
    fi
    sleep 30
done
