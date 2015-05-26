#!/bin/sh

killall speech-dispatcher

sleep 2

python mavproxy.py --master=localhost:14550 --baudrate=115200 target-system=55 --aircraft=null --target-component=1 --source-system=252 --streamrate=1 --speech



