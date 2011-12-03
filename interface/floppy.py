#!/usr/bin/env python
import serial
import collections

serial=serial.Serial(port="/dev/ttyUSB1",baudrate=115200,timeout=1)

ALIGN=0
STOP=1
PLAY=2

periods=collections.OrderedDict()
startoctave=3

notes="C C# D D# E F F# G G# A A# B".split(" ")
def tune(factor=1):
	Corg=60300/factor
	difference=0.9439953810623557
	for octaveid,octave in enumerate(range(startoctave,10)):
		for noteid,note in enumerate(notes):
			period=int(Corg* difference**((octaveid*len(notes))+noteid))
			periods[note+str(octave-1)]=period
	print periods
tune(0.986)

def notename(noteid):
	"""Converts midi note id to note name, Ex: C0->0"""
	for listnoteid, notename in enumerate(periods):
		listnoteid+=startoctave*len(notes)
		if listnoteid==noteid:
			return notename
	raise ValueError("Floppy drive can't produce %s." % noteid)

def play(note):
	try:
		period=periods[note]
	except KeyError:
		period=periods[notename(note)]
	print note, period
	d0=(period&0xFF00)>>8
	d1=period&0xFF
	data=bytearray([PLAY,d0,d1])
	serial.write(data)

def stop():
	serial.write(bytearray([STOP]))

if __name__=="__main__":
	import time
	play("C3")
	time.sleep(0.5)
	stop()