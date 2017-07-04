#!/usr/bin/env bash

#Only push to active_cameras
cams="active_cameras.txt"
while read -r line #|| [[ -n $line ]]
do
    #First, stop pepi if currently running
    ssh -i keys/pepi_rsa pi@"$line" 'ps -ef | grep "pepi.sh" | grep -v grep | awk '\''{print $2}'\'' | xargs kill' < /dev/null
    ssh -i keys/pepi_rsa pi@"$line" 'ps -ef | grep "server.py" | grep -v grep | awk '\''{print $2}'\'' | xargs kill' < /dev/null
    #Then push to the server
    echo "Pushing to $line..."
    rsync -rzt -e "ssh -i keys/pepi_rsa" * pi@"$line":/home/pi/pibox
    #Check if successful push
    if [ "$?" -eq "0" ]
    then
        echo "Successful push to $line"
        #Start up the server again detached from SSH session
        ssh -i keys/pepi_rsa pi@"$line" 'nohup ~/pibox/pepi.sh < /dev/null > std.out 2> std.err &' < /dev/null
        echo "START: $line's server"
    else
        echo "Error while pushing to $line"
    fi
done < "$cams"