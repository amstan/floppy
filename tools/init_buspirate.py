#!/usr/bin/env python
import serial
import collections

serial=serial.Serial(port="/dev/ttyUSB0",baudrate=115200,timeout=0.2)

data="""
m
3
5
1
1
1
2
W
(1)
y
"""

import time
for line in data.split("\n"):
	serial.write(line+"\n")
	print "(sending) %s" % line
	print serial.read(1000)