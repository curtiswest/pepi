#!/bin/bash
while read p; 
do sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no pi@$p "sudo shutdown now" 
done < active_cameras.txt
