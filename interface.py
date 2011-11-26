#!/usr/bin/env python
import serial
import collections

serial=serial.Serial(port="/dev/ttyUSB0",baudrate=115200,timeout=1)

ALIGN=0
STOP=1
PLAY=2

notes="C C# D D# E F F# G G# A A# B".split(" ")
periods=collections.OrderedDict()
def tune(factor=1):
	C2=60300/factor
	difference=0.9439953810623557
	for octaveid,octave in enumerate(range(2,10)):
		for noteid,note in enumerate(notes):
			periods[note+str(octave)]=int(C2* difference**((octaveid*len(notes))+noteid))
	print periods
tune(0.986)

def play(note):
	period=periods[note]
	print note, period
	d0=(period&0xFF00)>>8
	d1=period&0xFF
	data=bytearray([PLAY,d0,d1])
	serial.write(data)

def stop():
	serial.write(bytearray([STOP]))


import time
from midi import *
import sys

track=0
channel=1
m = MidiFile() 
m.open(sys.argv[1])
m.read() 
m.close()
a=""
periodslist=periods.items()
playing=None
print m
try:
	for event in m.tracks[track].events:
		if event.type=="DeltaTime":
			print event.time
			time.sleep(event.time/1000.0)
		elif event.type=="NOTE_OFF":
			if event.channel==channel:
				playing=None
				print "stop"
				stop()
		elif event.type=="NOTE_ON":
			if event.channel==channel:
				if event.pitch>playing:
					playing=event.pitch
					play(periodslist[event.pitch-36][0])
		else:
			print event
except KeyboardInterrupt:
	stop()