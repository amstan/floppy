#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jacklib
import Queue
from floppy import *

# Globals
global jack_midi_in_port, jack_midi_in_data
jack_client = None
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
	jack_midi_in_port = jacklib.port_register(jack_client, "midi_in", jacklib.DEFAULT_MIDI_TYPE, jacklib.PortIsInput, 0)
	jacklib.set_process_callback(jack_client, jack_process_callback, 0)
	
	jacklib.activate(jack_client)
	
	noteplaying=None
	
	while 1:
		try:
			mode, note, velo = jack_midi_in_data.get(True,1)
			print (mode,note,velo)
			if mode==144:
				play(note)
				noteplaying=note
			elif mode==128:
				if note==noteplaying:
					stop()
					print "stopping %s" % note
				else:
					print "not stopping: %s!=%s" % (note, noteplaying)
			else:
				print "ignoring",mode,note,velo
		except Queue.Empty:
			pass
		except ValueError as e:
			print e
	
	# Close Jack
	if (jack_client):
		jacklib.deactivate(jack_client)
		jacklib.client_close(jack_client)