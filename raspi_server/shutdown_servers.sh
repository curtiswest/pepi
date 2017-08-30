#!/usr/bin/env bash

#Only push to active_cameras
cams="server_ips.txt"
arg1="$1"
while read -r line #|| [[ -n $line ]]
do
    echo "Shutting down $line..."
    ssh -i keys/pepi_rsa pi@"$line" 'sudo poweroff' < /dev/null > /dev/null
done < "$cams"