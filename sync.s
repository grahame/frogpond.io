while true; do
    echo "sync from pi"
    rsync -av --partial --progress --exclude '*jpg~' pi@frogpond2.local:snaps/ ~/snaps/
    if [ -d /Volumes/Frogpond/snaps/ ]; then
        echo "sync to external disk"
        rsync -av ~/snaps/ /Volumes/Frogpond/snaps/
        ls ~/snaps/2???-??-??/ |
            ssh pi@frogpond2.local ~/code/frogpond.io/remove-files.sh
    fi
    sleep 30
done
