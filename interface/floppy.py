#!/usr/bin/env python
import serial
import collections

serial=serial.Serial(port="/dev/ttyACM0",baudrate=9600,timeout=1)

ALIGN=0
STOP=1
PLAY=2
INSTR=3
TOGGLE_DIR=4
RESET=5

periods=range(128)
def tune(factor=1):
	firstC=60300/factor
	difference=0.9439953810623557
	for noteid, _ in enumerate(periods):
		periods[noteid]=int(firstC * difference**(noteid))
	print periods
tune(0.986)

def notename(noteid):
	"""Converts midi note id to note name, Ex: 24->C1"""
	notes="C C# D D# E F F# G G# A A# B".split(" ")
	
	octave=noteid/12-1
	note=noteid%12
	
	return "%s%s" % (notes[note],octave)

current_period=0
def play(note):
	if (current_instr==INSTR_VIOLIN) and (note>44):
		raise ValueError("Violin cannot play that high! %s(%d)" % (notename(note), note))
	if (current_instr==INSTR_OSCILATE) and (note>49):
		raise ValueError("Oscillator cannot play that high! %s(%d)" % (notename(note), note))
	
	period=periods[note]
	
	print "%s(%d) - %d" % (notename(note), note, period)
	
	instr(current_instr)
	if current_instr==INSTR_VIOLIN:
		toggle_dir()
	
	global current_period
	current_period=period
	
	play_period(period)

def play_period(period):
	if(period>2**16):
		raise ValueError("Period for %s(%d) too big!" % (notename(note), note))
	
	d0=(period&0xFF00)>>8
	d1=period&0xFF
	data=bytearray([PLAY,d0,d1])
	serial.write(data)

def stop():
	serial.write(bytearray([STOP]))

INSTR_OSCILATE = 0
INSTR_VIOLIN = 1
def instr(target_instr):
	global current_instr
	current_instr=target_instr
	serial.write(bytearray([INSTR,target_instr]))
instr(INSTR_OSCILATE)

def toggle_dir():
	serial.write(bytearray([TOGGLE_DIR]))

def reset():
	serial.write(bytearray([RESET]))

if __name__=="__main__":
	"""Do a simple test"""
	import time
	try:
		note=40
		while 1:
			play(note)
			note+=1
			raw_input()
	except KeyboardInterrupt:
		stop()
	except Exception as e:
		print e