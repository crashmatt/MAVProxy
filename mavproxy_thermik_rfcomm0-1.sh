#!/bin/sh

killall speech-dispatcher

sleep 2

python mavproxy.py --master=/dev/rfcomm0 --out=/dev/rfcomm1 --baudrate=115200 target-system=55 --aircraft=Thermik --target-component=1 --source-system=252 --out=localhost:14550 --streamrate=1





