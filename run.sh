#!/bin/bash

while : ; do
    echo run
    python /srv/metroterm/adfc-tour-to-vadb.py
    echo sleep
    find /tmp/adfc* -mtime +1 -delete
    sleep 20
    #sleep 43200  # = 12h in seconds
done
