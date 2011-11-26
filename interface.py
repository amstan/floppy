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

def song():
	song="""
		E4, E4, F4, G4, G4, F4, E4, D4, C4, C4, D4, E4, E4, D4, D4,
		E4, E4, F4, G4, G4, F4, E4, D4, C4, C4, D4, E4, D4, C4, C4,
	""".replace("\t","").replace("\n","").replace(" ","").split(",")
	for note in song:
		try:
			play(note)
			time.sleep(0.49)
			stop()
			time.sleep(0.01)
			
		except Exception as e:
			print e
song()