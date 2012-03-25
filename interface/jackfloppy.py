#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import jacklib
import Queue
from floppy import *
import floppy

MIDI_MASK   =0b11110000
MIDI_NOTEOFF=0b10000000
MIDI_NOTEON =0b10010000
MIDI_PITCH  =0b11100000
MIDI_MODE   =0b10110000

# Globals
jack_client = None
global jack_midi_in_port, jack_midi_in_data
jack_midi_in_port = None
jack_midi_in_data = Queue.Queue(1024)

def jack_process_callback(nframes, arg):
	try:
		global jack_midi_in_port, jack_midi_in_data
		
		# MIDI In
		midi_in_buffer = jacklib.port_get_buffer(jack_midi_in_port, nframes)
		event_count = jacklib.midi_get_event_count(midi_in_buffer)
		
		if (event_count > 0):
			event = jacklib.jack_midi_event_t()
			
			for i in range(event_count):
				if (jacklib.midi_event_get(jacklib.pointer(event), midi_in_buffer, i) == 0):
					data = jacklib.translate_midi_event_buffer(event.buffer)
					
					if (len(data) == 1):
						jack_midi_in_data.put_nowait((data[0], 0, 0))
					
					elif (len(data) == 2):
						jack_midi_in_data.put_nowait((data[0], data[1], 0))
					
					elif (len(data) == 3):
						jack_midi_in_data.put_nowait((data[0], data[1], data[2]))
					
					if (jack_midi_in_data.full()):
						break
			
			del event
	except Exception as e:
		print e
	return 0

if __name__ == '__main__':
	# Start jack
	jack_client = jacklib.client_open("Floppy Drive", jacklib.NullOption, 0)
	jack_midi_in_port = jacklib.port_register(jack_client, "midi", jacklib.DEFAULT_MIDI_TYPE, jacklib.PortIsInput, 0)
	jacklib.set_process_callback(jack_client, jack_process_callback, 0)
	
	jacklib.activate(jack_client)
	
	noteplaying=None
	
	pitches=[]
	
	while 1:
		try:
			mode, note, velo = jack_midi_in_data.get(True,1)
			
			if(note<67):
				#below
				if(not int(sys.argv[2])):
					continue
				print "below"
				note-=36
				note+=12
			else:
				#above
				if(int(sys.argv[2])):
					continue
				print "above"
				note-=72-24
			
			if (mode&MIDI_MASK)==MIDI_NOTEON:
				play(note)
				noteplaying=note
			
			elif (mode&MIDI_MASK)==MIDI_NOTEOFF:
				if note==noteplaying:
					stop()
			
			elif (mode&MIDI_MASK)==MIDI_PITCH:
				pitch=velo*256+note
				
				if pitch==0:
					#apparently this is a no bend somehow...
					pitch=0x4000
				
				pitch-=0x4000
				pitch*=1.0
				pitch/=0x18000
				print "Pitch-bend", pitch
				pitch=2**pitch
				
				play_period(int(floppy.current_period/pitch))
			elif (mode&MIDI_MASK)==MIDI_MODE:
				if note in (64,120,121,123):
					#print "Everything off(%s) on channel %s." % (note, mode&(~MIDI_MASK))
					stop()
			
			else:
				print "ignoring",mode,note,velo
				pass
		except Queue.Empty:
			pass
		except ValueError as e:
			print e
		except KeyboardInterrupt:
			stop()
			raise
	
	# Close Jack
	if (jack_client):
		jacklib.deactivate(jack_client)
		jacklib.client_close(jack_client)