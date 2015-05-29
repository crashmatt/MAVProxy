#!/bin/sh
echo "starting mavproxy launch"

#export DISPLAY=:0

cd /home/matt/Documents/AeroThermik/Tools/MAVLink/MAVProxy

while  :
do
	
	
	if screen -list | grep -q mavproxy
	then
		echo "mavproxy screen is running"
		screen -r mavproxy
	else
		screen -S mavproxy ./mavproxy_null_noconn.sh
	fi
	sleep 5
done

#until screen -S mavproxy ./mavproxy_null_noconn.sh; do
#	echo "mavproxy stopped. Respawning " >&2
#	sleep 1
#done


