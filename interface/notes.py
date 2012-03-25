#!/usr/bin/env python2
import math

octave="C C# D D# E F F# G G# A A# B".split()

class Note(object):
	def __init__(self,noteid):
		self.noteid=noteid
	
	def __repr__(self):
		return "Note(%s)<%s>" % (self.noteid, self)
	
	def __str__(self):
		return "%s%s" % (octave[self.noteid%12],self.noteid/12-1)
	
	def __add__(self,other):
		try:
			othernoteid=other.noteid
		except:
			othernoteid=other
		return Note(self.noteid+othernoteid)
	
	def __cmp__(self,other):
		try:
			othernoteid=other.noteid
		except:
			othernoteid=other
		return cmp(self.noteid,othernoteid)
	
	def __sub__(self,other):
		try:
			othernoteid=other.noteid
		except:
			othernoteid=other
		return Note(self.noteid-othernoteid)
	
	@property
	def frequency(self):
		return math.pow(2,(self.noteid-69.0)/12)*440
	
	def period(self,ClockFreq=1000000):
		"""Returns how many clock cycles for a specific clock frequency. Frequency is automatically divided by 2 because this is for the step, not for the direction."""
		ClockFreq/=2.0
		
		return ClockFreq/self.frequency

if __name__=="__main__":
	for i in range(128):
		note=Note(i)
		print "%d\t%r\t%f\t%d" % (i,note,note.frequency,note.period())