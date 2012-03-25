#!/usr/bin/env python2
from notes import *

ALIGN=0
STOP=1
PLAY=2
INSTR=3
TOGGLE_DIR=4
RESET=5

class Floppy(object):
	FCPU=16000000
	TIMERCLOCK=FCPU
	TIMERCLOCK/=8 #prescaler
	TIMERCLOCK/=2 #still too big
	
	def __init__(self,port="/dev/ttyACM0",reset=True):
		import serial
		self.port=port
		self.serial=serial.Serial(port=self.port,baudrate=9600,timeout=1)
		self.serial.flush()
		
		if(reset):
			self.reset()
		
		self.instrument=0
	
	def __repr__(self):
		return "Floppy(%r)" % (self.port)
	
	def sync(self,times=3):
		"""Syncs the serial protocol. WARNING: don't spam the line, new bytes are discarded by something for some reason."""
		self.serial.write(bytearray((ALIGN,)*times))
		self.serial.flush()
		self.serial.write(bytearray((ALIGN,)))
	
	def reset(self):
		import time
		
		self.sync()
		time.sleep(0.1)
		
		print "Resetting %r" % (self)
		self.serial.write(bytearray((RESET,)))
		time.sleep(3)
		
		self.sync()
	
	def stop(self):
		self.serial.write(bytearray((STOP,)))
		self._note=None
	
	def play_period(self,period):
		period=int(period)
		if(period>2**16):
			raise ValueError("Period(%d) for %r too big!" % (period,self))
		
		d0=(period&0xFF00)>>8
		d1=period&0xFF
		data=bytearray((PLAY,d0,d1))
		self.serial.write(data)
	
	def play(self,note):
		if (note>128):
			raise ValueError("%r cannot play that high! %r" % (self,note))
		
		self._note=note
		self._period=note.period(self.TIMERCLOCK)
		print "%r - %d" % (note,self._period)
		
		if self.instrument=="violin":
			self.toggle_dir()
		
		self.play_period(self._period)
	
	def pitchbend(self,pitch):
		"""Pitchbends according to a midi pitchbend value."""
		if pitch==0:
			#apparently this is a no bend somehow...
			pitch=0x4000
		
		pitch-=0x4000
		pitch*=1.0
		pitch/=0x18000
		pitch=2**pitch
		
		self.play_period(self._period/pitch)
		print "Pitchbending %s*%2.2f" % (self._note,pitch)
	
	instruments=["oscillate","violin"]
	
	@property
	def instrument(self):
		return self.instruments[self._instrument]
		
	@instrument.setter
	def instrument(self,value):
		try:
			value=self.instruments.index(value)
		except ValueError:
			if value not in range(len(self.instruments)):
				raise ValueError("No such instrument(%r) exists." % value)
		
		try:
			if self._instrument!=value:
				print "Setting instrument to %s." % (self.instrument)
		except:
			pass
		finally:
			self._instrument=value
		
		self.serial.write(bytearray((INSTR,self._instrument)))
	
	def toggle_dir(self):
		self.serial.write(bytearray((TOGGLE_DIR,)))

if __name__=="__main__":
	PITCH_DEMO=True
	
	import time,sys
	floppy=Floppy(port=sys.argv[1],reset=False)
	try:
		while 1:
			for noteid in range(0,128):
				try:
					#play next note
					note=Note(noteid)
					floppy.play(note)
					
					#wait for key
					raw_input()
					
					if PITCH_DEMO:
						for pitch in range(0x4000,0x6000,0x100):
							floppy.pitchbend(pitch)
							time.sleep(0.01)
						time.sleep(0.2)
						floppy.sync()
					else:
						floppy.stop()
						time.sleep(0.05)
				except Exception as e:
					print repr(e)
			floppy.sync()
	finally:
		print "Stopping %r" % (floppy)
		time.sleep(0.5)
		floppy.sync()
		floppy.stop()
		floppy.serial.flush()