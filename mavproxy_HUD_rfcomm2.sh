#!/bin/sh

python mavproxy.py --master=localhost:14550 --out=/dev/rfcomm2 --baudrate=115200 target-system=55 --aircraft=HUD --target-component=1 --source-system=252 --streamrate=1



