#!/bin/sh

python mavproxy.py --master=/dev/ttyUSB0 --baudrate=57600 target-system=55 --aircraft=Thermik --target-component=1 --source-system=252 --out=localhost:14550 --streamrate=1



