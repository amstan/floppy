#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
from ctypes import *
from sys import platform, version_info

# Test for python 3.x
if (version_info >= (3,0)):
  PYTHON3 = True
else:
  PYTHON3 = False

# Load JACK shared library
try:
  if (platform == 'win32' or platform == 'win64'):
    jacklib = cdll.LoadLibrary("libjack.dll")
  else:
    jacklib = cdll.LoadLibrary("libjack.so.0")
except:
  jacklib = None

# Defines
MAX_FRAMES = 4294967295
LOAD_INIT_LIMIT = 1024

DEFAULT_AUDIO_TYPE = "32 bit float mono audio"
DEFAULT_MIDI_TYPE  = "8 bit raw midi"

# Jack Options
NullOption    = 0x00
NoStartServer = 0x01
UseExactName  = 0x02
ServerName    = 0x04
LoadName      = 0x08
LoadInit      = 0x10
SessionID     = 0x20
OpenOptions   = SessionID|ServerName|NoStartServer|UseExactName
LoadOptions   = LoadInit|LoadName|UseExactName

# Jack Status
Failure       = 0x01
InvalidOption = 0x02
NameNotUnique = 0x04
ServerStarted = 0x08
ServerFailed  = 0x10
ServerError   = 0x20
NoSuchClient  = 0x40
LoadFailure   = 0x80
InitFailure   = 0x100
ShmFailure    = 0x200
VersionError  = 0x400
BackendError  = 0x800
ClientZombie  = 0x1000

# Jack Latency Callback Mode
CaptureLatency  = 0 # FIXME
PlaybackLatency = 1

# Jack Port Flags
PortIsInput    = 0x1
PortIsOutput   = 0x2
PortIsPhysical = 0x4
PortCanMonitor = 0x8
PortIsTerminal = 0x10

# Transport states
TransportStopped     = 0
TransportRolling     = 1
TransportLooping     = 2
TransportStarting    = 3
TransportNetStarting = 4

# Optional struct jack_position_t fields
PositionBBT      = 0x10
PositionTimecode = 0x20
BBTFrameOffset   = 0x40
AudioVideoRatio  = 0x80
VideoFrameOffset = 0x100
POSITION_MASK    = PositionBBT|PositionTimecode

# Optional struct jack_position_bits_t/jack_transport_info_t fields
TransportState    = 0x1
TransportPosition = 0x2
TransportLoop     = 0x4
TransportSMPTE    = 0x8
TransportBBT      = 0x10

# ? Not in the API:
AUDIO = 0
MIDI  = 1


# Types
jack_shmsize_t = c_int32
jack_nframes_t = c_uint32
jack_time_t = c_uint64
jack_intclient_t = c_uint64
jack_port_t = c_void_p #_jack_port
jack_client_t = c_void_p #_jack_client
jack_port_id_t = c_uint32
jack_port_type_id_t = c_uint32
jack_default_audio_sample_t = c_float
jack_unique_t = c_uint64
jack_native_thread_t = c_long #HANDLE/pthread_t
jack_midi_data_t = c_char


# TODO - Enums
jack_options_t = c_int
jack_status_t = c_int
jack_latency_callback_mode_t = c_int
jack_transport_state_t = c_int
jack_position_bits_t = c_int
jack_transport_bits_t = c_int


# Structs
class jack_latency_range_t(Structure):
  _fields_ = [
    ("min", jack_nframes_t),
    ("max", jack_nframes_t)
  ]
#jack_latency_range_t = _jack_latency_range_t()

class jack_position_t(Structure):
  _fields_ = [
    ("unique_1", jack_unique_t),
    ("usecs", jack_time_t),
    ("frame_rate", jack_nframes_t),
    ("frame", jack_nframes_t),
    ("valid", jack_position_bits_t),
    ("bar", c_int32),
    ("beat", c_int32),
    ("tick", c_int32),
    ("bar_start_tick", c_double),
    ("beats_per_bar", c_float),
    ("beat_type", c_float),
    ("ticks_per_beat", c_double),
    ("beats_per_minute", c_double),
    ("frame_time", c_double),
    ("next_time", c_double),
    ("bbt_offset", jack_nframes_t),
    ("audio_frames_per_video_frame", c_float),
    ("video_offset", jack_nframes_t),
    ("padding", ARRAY(c_int32, 7)),
    ("unique_2", jack_unique_t)
  ]
#jack_position_t = _jack_position_t()

class jack_transport_info_t(Structure):
  _fields_ = [
    ("frame_rate", jack_nframes_t),
    ("usecs", jack_time_t),
    ("valid", jack_transport_bits_t),
    ("transport_state", jack_transport_state_t),
    ("frame", jack_nframes_t),
    ("loop_start", jack_nframes_t),
    ("loop_end", jack_nframes_t),
    ("smpte_offset", c_long),
    ("smpte_frame_rate", c_float),
    ("bar", c_int),
    ("beat", c_int),
    ("tick", c_int),
    ("bar_start_tick", c_double),
    ("beats_per_bar", c_float),
    ("beat_type", c_float),
    ("ticks_per_beat", c_double),
    ("beats_per_minute", c_double),
  ]
#jack_transport_info_t = _jack_transport_info_t()

class jack_midi_event_t(Structure):
  _fields_ = [
    ("time", jack_nframes_t),
    ("size", c_size_t),
    ("buffer", c_char_p), #POINTER(jack_midi_data_t)
  ]
#jack_midi_event_t = _jack_midi_event_t()


# Special Callback defines
global LatencyCallback, ProcessCallback, ThreadCallback, ThreadInitCallback, GraphOrderCallback, XRunCallback
global BufferSizeCallback, SampleRateCallback, PortRegistrationCallback, ClientRegistrationCallback, PortConnectCallback, PortRenameCallback
global FreewheelCallback, ShutdownCallback, InfoShutdownCallback, SyncCallback, TimebaseCallback, SessionCallback


# Internal C char** -> Python list conversion
def __pointer_to_list(list_p):
  final_list = []
  i = 0

  if (not list_p):
    return final_list

  while (True):
    new_char_p = list_p[i]
    if (new_char_p):
      final_list.append(str(new_char_p))
    else:
      break
    i += 1

  jack_free(list_p)
  return final_list

# External helper funtions
def translate_audio_port_buffer(void_p):
  return cast(void_p, POINTER(jack_default_audio_sample_t))

def translate_midi_event_buffer(void_p):
  if (not void_p):
    return list()

  if (len(void_p) == 1):
    if (PYTHON3):
      return (int(void_p),)
    else:
      return (ord(void_p),)

  elif (len(void_p) == 2):
    if (PYTHON3):
      return (int(void_p[0]), int(void_p[1]))
    else:
      return (ord(void_p[0]), ord(void_p[1]))

  elif (len(void_p) == 3):
    if (PYTHON3):
      return (int(void_p[0]), int(void_p[1]), int(void_p[2]))
    else:
      return (ord(void_p[0]), ord(void_p[1]), ord(void_p[2]))

  elif (len(void_p) == 4):
    if (PYTHON3):
      return (int(void_p[0]), int(void_p[1]), int(void_p[2]), int(void_p[3]))
    else:
      return (ord(void_p[0]), ord(void_p[1]), ord(void_p[2]), ord(void_p[3]))

  else:
    return list()

def encode_midi_data(d1, d2=None, d3=None, d4=None):
  if (d2 == None):
    return "%s" % (chr(d1))
  elif (d3 == None):
    return "%s%s" % (chr(d1), chr(d2))
  elif (d4 == None):
    return "%s%s%s" % (chr(d1), chr(d2), chr(d3))
  else:
    return "%s%s%s%s" % (chr(d1), chr(d2), chr(d3), chr(d4))


# Functions

def get_version(): # FIXME - does not work!
  major_ptr = c_int(0)
  minor_ptr = c_int(0)
  micro_ptr = c_int(0)
  proto_ptr = c_int(0)
  jacklib.jack_get_version.argtypes = [POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int)]
  jacklib.jack_get_version.restype = None
  jacklib.jack_get_version(pointer(major_ptr), pointer(minor_ptr), pointer(micro_ptr), pointer(proto_ptr))
  return (major_ptr.value, minor_ptr.value, micro_ptr.value, proto_ptr.value)

def get_version_string():
  jacklib.jack_get_version_string.argtypes = None
  jacklib.jack_get_version_string.restype = c_char_p
  return jacklib.jack_get_version_string()

def client_open(client_name, options, status):
  if (PYTHON3): client_name = client_name.encode()
  if (options == None): options = 0
  if (status == None): status = 0
  jacklib.jack_client_open.argtypes = [c_char_p, c_int, c_int]
  jacklib.jack_client_open.restype = jack_client_t
  return jacklib.jack_client_open(client_name, options, status)

def client_new(client_name):
  if (PYTHON3): client_name = client_name.encode()
  jacklib.jack_client_new.argtypes = [c_char_p]
  jacklib.jack_client_new.restype = jack_client_t
  return jacklib.jack_client_new(client_name)

def client_close(client):
  jacklib.jack_client_close.argtypes = [jack_client_t]
  jacklib.jack_client_close.restype = c_int
  return jacklib.jack_client_close(client)

def client_name_size():
  jacklib.jack_client_name_size.argtypes = None
  jacklib.jack_client_name_size.restype = c_int
  return jacklib.jack_client_name_size()

def get_client_name(client):
  jacklib.jack_get_client_name.argtypes = [jack_client_t]
  jacklib.jack_get_client_name.restype = c_char_p
  return jacklib.jack_get_client_name(client)

def internal_client_new(client_name, load_name, load_init):
  if (PYTHON3): client_name = client_name.encode()
  if (PYTHON3): load_name = load_name.encode()
  if (PYTHON3): load_init = load_init.encode()
  jacklib.jack_internal_client_new.argtypes = [c_char_p, c_char_p, c_char_p]
  jacklib.jack_internal_client_new.restype = c_int
  return jacklib.jack_internal_client_new(client_name, load_name, load_init)

def internal_client_close(client_name):
  if (PYTHON3): client_name = client_name.encode()
  jacklib.jack_internal_client_close.argtypes = [c_char_p]
  jacklib.jack_internal_client_close.restype = None
  return jacklib.jack_internal_client_close(client_name)

def activate(client):
  jacklib.jack_activate.argtypes = [jack_client_t]
  jacklib.jack_activate.restype = c_int
  return jacklib.jack_activate(client)

def deactivate(client):
  jacklib.jack_deactivate.argtypes = [jack_client_t]
  jacklib.jack_deactivate.restype = c_int
  return jacklib.jack_deactivate(client)

def get_client_pid(name):
  if (PYTHON3): name = name.encode()
  jacklib.jack_get_client_pid.argtypes = [c_char_p]
  jacklib.jack_get_client_pid.restype = c_int
  return jacklib.jack_get_client_pid(name)

def client_thread_id(client):
  jacklib.jack_client_thread_id.argtypes = [jack_client_t]
  jacklib.jack_client_thread_id.restype = jack_native_thread_t
  return jacklib.jack_client_thread_id(client)

def is_realtime(client):
  jacklib.jack_is_realtime.argtypes = [jack_client_t]
  jacklib.jack_is_realtime.restype = c_int
  return jacklib.jack_is_realtime(client)


# Non Callback API

def thread_wait(client):
  jacklib.jack_thread_wait.argtypes = [jack_client_t, c_int]
  jacklib.jack_thread_wait.restype = jack_nframes_t
  return jacklib.jack_thread_wait(client, status)

def cycle_wait(client):
  jacklib.jack_cycle_wait.argtypes = jack_client_t
  jacklib.jack_cycle_wait.restype = jack_nframes_t
  return jacklib.jack_cycle_wait(client)

def cycle_signal(client, status):
  jacklib.jack_cycle_signal.argtypes = [jack_client_t, status]
  jacklib.jack_cycle_signal.restype = None
  return jacklib.jack_cycle_signal(client, status)

def set_process_thread(client, thread_callback, arg=None):
  global ThreadCallback
  ThreadCallback = CFUNCTYPE(c_int, c_void_p)(thread_callback)
  jacklib.jack_set_process_thread.restype = c_int
  return jacklib.jack_set_process_thread(client)


# Client Callbacks

def set_thread_init_callback(client, thread_init_callback, arg=None):
  global ThreadInitCallback
  ThreadInitCallback = CFUNCTYPE(c_int, c_void_p)(thread_init_callback)
  jacklib.jack_set_thread_init_callback.restype = c_int
  return jacklib.jack_set_thread_init_callback(client, ThreadInitCallback, arg)

def on_shutdown(client, shutdown_callback, arg=None):
  global ShutdownCallback
  ShutdownCallback = CFUNCTYPE(c_int, c_void_p)(shutdown_callback)
  jacklib.jack_on_shutdown(client, ShutdownCallback, arg)

def on_info_shutdown(client, shutdown_callback, arg=None):
  global InfoShutdownCallback
  InfoShutdownCallback = CFUNCTYPE(c_int, c_int, c_char_p, c_void_p)(shutdown_callback)
  jacklib.jack_on_info_shutdown(client, InfoShutdownCallback, arg)

def set_process_callback(client, process_callback, arg=None):
  global ProcessCallback
  ProcessCallback = CFUNCTYPE(c_int, c_int, c_void_p)(process_callback)
  jacklib.jack_set_process_callback.restype = c_int
  return jacklib.jack_set_process_callback(client, ProcessCallback, arg)

def set_freewheel_callback(client, freewheel_callback, arg=None):
  global FreewheelCallback
  FreewheelCallback = CFUNCTYPE(c_int, c_int, c_void_p)(freewheel_callback)
  jacklib.jack_set_freewheel_callback.restype = c_int
  return jacklib.jack_set_freewheel_callback(client, FreewheelCallback, arg)

def set_buffer_size_callback(client, buffer_size_callback, arg=None):
  global BufferSizeCallback
  BufferSizeCallback = CFUNCTYPE(c_int, c_int, c_void_p)(buffer_size_callback)
  jacklib.jack_set_buffer_size_callback.restype = c_int
  return jacklib.jack_set_buffer_size_callback(client, BufferSizeCallback, arg)

def set_sample_rate_callback(client, srate_callback, arg=None):
  global SampleRateCallback
  SampleRateCallback = CFUNCTYPE(c_int, c_int, c_void_p)(srate_callback)
  jacklib.jack_set_sample_rate_callback.restype = c_int
  return jacklib.jack_set_sample_rate_callback(client, SampleRateCallback, arg)

def set_client_registration_callback(client, registration_callback, arg=None):
  global ClientRegistrationCallback
  ClientRegistrationCallback = CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)(registration_callback)
  jacklib.jack_set_client_registration_callback.restype = c_int
  return jacklib.jack_set_client_registration_callback(client, ClientRegistrationCallback, arg)

def set_port_registration_callback(client, registration_callback, arg=None):
  global PortRegistrationCallback
  PortRegistrationCallback = CFUNCTYPE(c_int, c_int, c_int, c_void_p)(registration_callback)
  jacklib.jack_set_port_registration_callback.restype = c_int
  return jacklib.jack_set_port_registration_callback(client, PortRegistrationCallback, arg)

def set_port_connect_callback(client, connect_callback, arg=None):
  global PortConnectCallback
  PortConnectCallback = CFUNCTYPE(c_int, c_int, c_int, c_int, c_void_p)(connect_callback)
  jacklib.jack_set_port_connect_callback.restype = c_int
  return jacklib.jack_set_port_connect_callback(client, PortConnectCallback, arg)

def set_port_rename_callback(client, rename_callback, arg=None):
  global PortRenameCallback
  PortRenameCallback = CFUNCTYPE(c_int, c_int, c_char_p, c_char_p, c_void_p)(rename_callback)
  jacklib.jack_set_port_rename_callback.restype = c_int
  return jacklib.jack_set_port_rename_callback(client, PortRenameCallback, arg)

def set_graph_order_callback(client, graph_callback, arg=None):
  global GraphOrderCallback
  GraphOrderCallback = CFUNCTYPE(c_int, c_void_p)(graph_callback)
  jacklib.jack_set_graph_order_callback.restype = c_int
  return jacklib.jack_set_graph_order_callback(client, GraphOrderCallback, arg)

def set_xrun_callback(client, xrun_callback, arg=None):
  global XRunCallback
  XRunCallback = CFUNCTYPE(c_int, c_void_p)(xrun_callback)
  jacklib.jack_set_xrun_callback.restype = c_int
  return jacklib.jack_set_xrun_callback(client, XRunCallback, arg)

def set_latency_callback(client, latency_callback, arg=None):
  global LatencyCallback
  LatencyCallback = CFUNCTYPE(c_int, c_void_p)(latency_callback)
  jacklib.jack_set_latency_callback.restype = c_int
  return jacklib.jack_set_latency_callback(client, LatencyCallback, arg)


# Server Client Control

def set_freewheel(client, onoff):
  jacklib.jack_set_freewheel.argtypes = [jack_client_t, c_int]
  jacklib.jack_set_freewheel.restype = c_int
  return jacklib.jack_set_freewheel(client, onoff)

def set_buffer_size(client, nframes):
  jacklib.jack_set_buffer_size.argtypes = [jack_client_t, jack_nframes_t]
  jacklib.jack_set_buffer_size.restype = c_int
  return jacklib.jack_set_buffer_size(client, nframes)

def get_sample_rate(client):
  jacklib.jack_get_sample_rate.argtypes = [jack_client_t]
  jacklib.jack_get_sample_rate.restype = jack_nframes_t
  return jacklib.jack_get_sample_rate(client)

def get_buffer_size(client):
  jacklib.jack_get_buffer_size.argtypes = [jack_client_t]
  jacklib.jack_get_buffer_size.restype = jack_nframes_t
  return jacklib.jack_get_buffer_size(client)

def engine_takeover_timebase(client):
  jacklib.jack_engine_takeover_timebase.argtypes = [jack_client_t]
  jacklib.jack_engine_takeover_timebase.restype = c_int
  return jacklib.jack_engine_takeover_timebase(client)

def cpu_load(client):
  jacklib.jack_cpu_load.argtypes = [jack_client_t]
  jacklib.jack_cpu_load.restype = c_float
  return jacklib.jack_cpu_load(client)


# Port Functions

def port_register(client, port_name, port_type, flags, buffer_size):
  if (PYTHON3): port_name = port_name.encode()
  if (PYTHON3): port_type = port_type.encode()
  jacklib.jack_port_register.argtypes = [jack_client_t, c_char_p, c_char_p, c_ulong, c_ulong]
  jacklib.jack_port_register.restype = jack_port_t
  return jacklib.jack_port_register(client, port_name, port_type, flags, buffer_size)

def port_unregister(client, port):
  jacklib.jack_port_unregister.argtypes = [jack_client_t, jack_port_t]
  jacklib.jack_port_unregister.restype = c_int
  return jacklib.jack_port_unregister(client, port)

def port_get_buffer(port, nframes):
  jacklib.jack_port_get_buffer.argtypes = [jack_port_t, jack_nframes_t]
  jacklib.jack_port_get_buffer.restype = c_void_p
  return jacklib.jack_port_get_buffer(port, nframes)

def port_name(port):
  jacklib.jack_port_name.argtypes = [jack_port_t]
  jacklib.jack_port_name.restype = c_char_p
  return jacklib.jack_port_name(port)

def port_short_name(port):
  jacklib.jack_port_short_name.argtypes = [jack_port_t]
  jacklib.jack_port_short_name.restype = c_char_p
  return jacklib.jack_port_short_name(port)

def port_flags(port):
  jacklib.jack_port_flags.argtypes = [jack_port_t]
  jacklib.jack_port_flags.restype = c_int
  return jacklib.jack_port_flags(port)

def port_type(port):
  jacklib.jack_port_type.argtypes = [jack_port_t]
  jacklib.jack_port_type.restype = c_char_p
  return jacklib.jack_port_type(port)

def port_type_id(port):
  jacklib.jack_port_type_id.argtypes = [jack_port_t]
  jacklib.jack_port_type_id.restype = jack_port_type_id_t
  return jacklib.jack_port_type_id(port)

def port_is_mine(client, port):
  jacklib.jack_port_is_mine.argtypes = [jack_client_t, jack_port_t]
  jacklib.jack_port_is_mine.restype = c_int
  return jacklib.jack_port_is_mine(client, port)

def port_connected(port):
  jacklib.jack_port_connected.argtypes = [jack_port_t]
  jacklib.jack_port_connected.restype = c_int
  return jacklib.jack_port_connected(port)

def port_connected_to(port, port_name):
  if (PYTHON3): port_name = port_name.encode()
  jacklib.jack_port_connected_to.argtypes = [jack_port_t, c_char_p]
  jacklib.jack_port_connected_to.restype = c_int
  return jacklib.jack_port_connected_to(port, port_name)

def port_get_connections(port):
  jacklib.jack_port_get_connections.argtypes = [jack_port_t]
  jacklib.jack_port_get_connections.restype = POINTER(c_char_p)
  list_p = jacklib.jack_port_get_connections(port)
  return __pointer_to_list(list_p)

def port_get_all_connections(client, port):
  jacklib.jack_port_get_all_connections.argtypes = [jack_client_t, jack_port_t]
  jacklib.jack_port_get_all_connections.restype = POINTER(c_char_p)
  list_p = jacklib.jack_port_get_all_connections(client, port)
  return __pointer_to_list(list_p)

def port_tie(src, dst):
  jacklib.jack_port_tie.argtypes = [jack_port_t, jack_port_t]
  jacklib.jack_port_tie.restype = c_int
  return jacklib.jack_port_tie(src, dst)

def port_untie(port):
  jacklib.jack_port_untie.argtypes = [jack_port_t]
  jacklib.jack_port_untie.restype = c_int
  return jacklib.jack_port_untie(port)

def port_set_name(port, port_name):
  if (PYTHON3): port_name = port_name.encode()
  jacklib.jack_port_set_name.argtypes = [jack_port_t, c_char_p]
  jacklib.jack_port_set_name.restype = c_int
  return jacklib.jack_port_set_name(port, port_name)

def port_set_alias(port, alias):
  if (PYTHON3): alias = alias.encode()
  jacklib.jack_port_set_alias.argtypes = [jack_port_t, c_char_p]
  jacklib.jack_port_set_alias.restype = c_int
  return jacklib.jack_port_set_alias(port, alias)

def port_unset_alias(port, alias):
  if (PYTHON3): alias = alias.encode()
  jacklib.jack_port_unset_alias.argtypes = [jack_port_t, c_char_p]
  jacklib.jack_port_unset_alias.restype = c_int
  return jacklib.jack_port_unset_alias(port, alias)

def port_get_aliases(port):
  # NOTE - this function has no 2nd argument in jacklib
  # Instead, aliases will be passed in return value, in form of (int ret, str alias1, str alias2)
  name_size = port_name_size()
  alias_type = c_char_p*2
  aliases = alias_type(" "*name_size, " "*name_size)

  jacklib.jack_port_get_aliases.argtypes = [jack_port_t, POINTER(ARRAY(c_char_p, 2))]
  jacklib.jack_port_get_aliases.restype = c_int

  ret = jacklib.jack_port_get_aliases(port, pointer(aliases))
  return (ret, aliases[0], aliases[1])

def port_request_monitor(port, onoff):
  jacklib.jack_port_request_monitor.argtypes = [jack_port_t, c_int]
  jacklib.jack_port_request_monitor.restype = c_int
  return jacklib.jack_port_request_monitor(port, onoff)

def port_request_monitor_by_name(client, port_name, onoff):
  if (PYTHON3): port_name = port_name.encode()
  jacklib.jack_port_request_monitor_by_name.argtypes = [jack_client_t, c_char_p, c_int]
  jacklib.jack_port_request_monitor_by_name.restype = c_int
  return jacklib.jack_port_request_monitor_by_name(client, port_name, onoff)

def port_ensure_monitor(port, onoff):
  jacklib.jack_port_ensure_monitor.argtypes = [jack_port_t, c_int]
  jacklib.jack_port_ensure_monitor.restype = c_int
  return jacklib.jack_port_ensure_monitor(port, onoff)

def port_monitoring_input(port):
  jacklib.jack_port_monitoring_input.argtypes = [jack_port_t]
  jacklib.jack_port_monitoring_input.restype = c_int
  return jacklib.jack_port_monitoring_input(port)

def connect(client, source_port, destination_port):
  if (PYTHON3): source_port = source_port.encode()
  if (PYTHON3): destination_port = destination_port.encode()
  jacklib.jack_connect.argtypes = [jack_client_t, c_char_p, c_char_p]
  jacklib.jack_connect.restype = c_int
  return jacklib.jack_connect(client, source_port, destination_port)

def disconnect(client, source_port, destination_port):
  if (PYTHON3): source_port = source_port.encode()
  if (PYTHON3): destination_port = destination_port.encode()
  jacklib.jack_disconnect.argtypes = [jack_client_t, c_char_p, c_char_p]
  jacklib.jack_disconnect.restype = c_int
  return jacklib.jack_disconnect(client, source_port, destination_port)

def port_disconnect(client, port):
  jacklib.jack_port_disconnect.argtypes = [jack_client_t, jack_port_t]
  jacklib.jack_port_disconnect.restype = c_int
  return jacklib.jack_port_disconnect(client, port)

def port_name_size():
  jacklib.jack_port_name_size.argtypes = None
  jacklib.jack_port_name_size.restype = c_int
  return jacklib.jack_port_name_size()

def port_type_size():
  jacklib.jack_port_type_size.argtypes = None
  jacklib.jack_port_type_size.restype = c_int
  return jacklib.jack_port_type_size()

def port_type_get_buffer_size(client, port_type):
  if (PYTHON3): port_type = port_type.encode()
  jacklib.jack_port_type_get_buffer_size.argtypes = [jack_client_t, c_char_p]
  jacklib.jack_port_type_get_buffer_size.restype = c_size_t
  return jacklib.jack_port_type_get_buffer_size(client, port_type)


# Latency Functions

def port_set_latency(port, nframes):
  jacklib.jack_port_set_latency.argtypes = [jack_port_t, jack_nframes_t]
  jacklib.jack_port_set_latency.restype = None
  jacklib.jack_port_set_latency(port, nframes)

def port_get_latency_range(port, mode, range_):
  jacklib.jack_port_get_latency_range.argtypes = [jack_port_t, jack_latency_callback_mode_t, POINTER(jack_latency_range_t)]
  jacklib.jack_port_get_latency_range.restype = None
  jacklib.jack_port_get_latency_range(port, mode, range_)

def port_set_latency_range(port, mode, range_):
  jacklib.jack_port_set_latency_range.argtypes = [jack_port_t, jack_latency_callback_mode_t, POINTER(jack_latency_range_t)]
  jacklib.jack_port_set_latency_range.restype = None
  jacklib.jack_port_set_latency_range(port, mode, range_)

def recompute_total_latencies():
  jacklib.recompute_total_latencies.argtypes = [jack_client_t]
  jacklib.recompute_total_latencies.restype = c_int
  return jacklib.recompute_total_latencies()

def port_get_latency(port):
  jacklib.jack_port_get_latency.argtypes = [jack_port_t]
  jacklib.jack_port_get_latency.restype = jack_nframes_t
  return jacklib.jack_port_get_latency(port)

def port_get_total_latency(client, port):
  jacklib.jack_port_get_total_latency.argtypes = [jack_client_t, jack_port_t]
  jacklib.jack_port_get_total_latency.restype = jack_nframes_t
  return jacklib.jack_port_get_total_latency(client, port)

def recompute_total_latency(client, port):
  jacklib.jack_recompute_total_latency.argtypes = [jack_client_t, jack_port_t]
  jacklib.jack_recompute_total_latency.restype = c_int
  return jacklib.jack_recompute_total_latency(client, port)


# Port Searching

def get_ports(client, port_name_pattern, type_name_pattern, flags):
  if (PYTHON3 and port_name_pattern): port_name_pattern = port_name_pattern.encode()
  if (PYTHON3 and type_name_pattern): type_name_pattern = type_name_pattern.encode()
  jacklib.jack_get_ports.argtypes = [jack_client_t, c_char_p, c_char_p, c_ulong]
  jacklib.jack_get_ports.restype = POINTER(c_char_p)
  list_p = jacklib.jack_get_ports(client, port_name_pattern, type_name_pattern, flags)
  return __pointer_to_list(list_p)

def port_by_name(client, port_name):
  if (PYTHON3): port_name = port_name.encode()
  jacklib.jack_port_by_name.argtypes = [jack_client_t, c_char_p]
  jacklib.jack_port_by_name.restype = jack_port_t
  return jacklib.jack_port_by_name(client, port_name)

def port_by_id(client, port_id):
  jacklib.jack_port_by_id.argtypes = [jack_client_t, jack_port_id_t]
  jacklib.jack_port_by_id.restype = jack_port_t
  return jacklib.jack_port_by_id(client, port_id)


# Time Functions

def frames_since_cycle_start(client):
  jacklib.jack_frames_since_cycle_start.argtypes = [jack_client_t]
  jacklib.jack_frames_since_cycle_start.restype = jack_nframes_t
  return jacklib.jack_frames_since_cycle_start(client)

def frame_time(client):
  jacklib.jack_frame_time.argtypes = [jack_client_t]
  jacklib.jack_frame_time.restype = jack_nframes_t
  return jacklib.jack_frame_time(client)

def last_frame_time(client):
  jacklib.jack_last_frame_time.argtypes = [jack_client_t]
  jacklib.jack_last_frame_time.restype = jack_nframes_t
  return jacklib.jack_last_frame_time(client)

def frames_to_time(client, nframes):
  jacklib.jack_frames_to_time.argtypes = [jack_client_t, jack_nframes_t]
  jacklib.jack_frames_to_time.restype = jack_time_t
  return jacklib.jack_frames_to_time(client, nframes)

def time_to_frames(client, time):
  jacklib.jack_time_to_frames.argtypes = [jack_client_t, jack_time_t]
  jacklib.jack_time_to_frames.restype = jack_nframes_t
  return jacklib.jack_time_to_frames(client, time)

def get_time():
  jacklib.jack_get_time.argtypes = [None]
  jacklib.jack_get_time.restype = jack_time_t
  return jacklib.jack_get_time()


# Error Output
# TODO


# Transport

def release_timebase(client):
  jacklib.jack_release_timebase.argtypes = [jack_client_t]
  jacklib.jack_release_timebase.restype = c_int
  return jacklib.jack_release_timebase(client)

def set_sync_callback(client, sync_callback, arg=None):
  global SyncCallback
  SyncCallback = CFUNCTYPE(c_int, c_int, POINTER(jack_position_t), c_void_p)(sync_callback)
  jacklib.jack_set_sync_callback.restype = c_int
  return jacklib.jack_set_sync_callback(client, SyncCallback, arg)

def set_sync_timeout(client, timeout):
  jacklib.jack_set_sync_timeout.argtypes = [jack_client_t, jack_time_t]
  jacklib.jack_set_sync_timeout.restype = c_int
  return jacklib.jack_set_sync_timeout(client, timeout)

def set_timebase_callback(client, conditional, timebase_callback, arg=None):
  global TimebaseCallback
  TimebaseCallback = CFUNCTYPE(c_int, c_int, c_int, POINTER(jack_position_t), c_int, c_void_p)(sync_callback)
  jacklib.jack_set_timebase_callback.restype = c_int
  return jacklib.jack_set_timebase_callback(client, conditional, TimebaseCallback, arg)

def transport_locate(client, frame):
  jacklib.jack_transport_locate.argtypes = [jack_client_t, jack_nframes_t]
  jacklib.jack_transport_locate.restype = c_int
  return jacklib.jack_transport_locate(client, frame)

def transport_query(client, pos=None):
  jacklib.jack_transport_query.restype = c_int
  if (pos != None):
    jacklib.jack_transport_query.argtypes = [jack_client_t, POINTER(jack_position_t)]
    return jacklib.jack_transport_query(client, pointer(pos))
  else:
    return jacklib.jack_transport_query(client, None)

def get_current_transport_frame(client):
  jacklib.jack_get_current_transport_frame.argtypes = [jack_client_t]
  jacklib.jack_get_current_transport_frame.restype = jack_nframes_t
  return jacklib.jack_get_current_transport_frame(client)

def transport_reposition(client, pos):
  jacklib.jack_transport_reposition.argtypes = [jack_client_t, POINTER(jack_position_t)]
  jacklib.jack_transport_reposition.restype = c_int
  return jacklib.jack_transport_reposition(client, pointer(pos))

def transport_start(client):
  jacklib.jack_transport_start.argtypes = [jack_client_t]
  jacklib.jack_transport_start.restype = None
  return jacklib.jack_transport_start(client)

def transport_stop(client):
  jacklib.jack_transport_stop.argtypes = [jack_client_t]
  jacklib.jack_transport_stop.restype = None
  return jacklib.jack_transport_stop(client)

def get_transport_info(client, tinfo):
  jacklib.jack_get_transport_info.argtypes = [jack_client_t, POINTER(jack_transport_info_t)]
  jacklib.jack_get_transport_info.restype = None
  return jacklib.jack_get_transport_info(client, pointer(tinfo))

def set_transport_info(client, tinfo):
  jacklib.jack_set_transport_info.argtypes = [jack_client_t, POINTER(jack_transport_info_t)]
  jacklib.jack_set_transport_info.restype = None
  return jacklib.jack_set_transport_info(client, pointer(tinfo))


# MIDI

def midi_get_event_count(port_buffer):
  jacklib.jack_midi_get_event_count.argtypes = [c_void_p]
  jacklib.jack_midi_get_event_count.restype = jack_nframes_t
  return jacklib.jack_midi_get_event_count(port_buffer)

def midi_event_get(event, port_buffer, event_index):
  jacklib.jack_midi_event_get.argtypes = [POINTER(jack_midi_event_t), c_void_p, jack_nframes_t]
  jacklib.jack_midi_event_get.restype = c_int
  return jacklib.jack_midi_event_get(event, port_buffer, event_index)

def midi_clear_buffer(port_buffer):
  jacklib.jack_midi_clear_buffer.argtypes = [c_void_p]
  jacklib.jack_midi_clear_buffer.restype = None
  return jacklib.jack_midi_clear_buffer(port_buffer)

def midi_max_event_size(port_buffer):
  jacklib.jack_midi_max_event_size.argtypes = [c_void_p]
  jacklib.jack_midi_max_event_size.restype = c_size_t
  return jacklib.jack_midi_max_event_size(port_buffer)

def midi_event_reserve(port_buffer, time, data_size):
  jacklib.jack_midi_event_reserve.argtypes = [c_void_p, jack_nframes_t, c_size_t]
  jacklib.jack_midi_event_reserve.restype = c_char_p #POINTER(jack_midi_event_t)
  return jacklib.jack_midi_event_reserve(port_buffer, time, data_size)

def midi_event_write(port_buffer, time, data, data_size):
  jacklib.jack_midi_event_write.argtypes = [c_void_p, jack_nframes_t, c_char_p, c_size_t] #POINTER(jack_midi_event_t)
  jacklib.jack_midi_event_write.restype = c_int
  return jacklib.jack_midi_event_write(port_buffer, time, data, data_size)

def midi_get_lost_event_count(port_buffer):
  jacklib.jack_midi_get_lost_event_count.argtypes = [c_void_p]
  jacklib.jack_midi_get_lost_event_count.restype = jack_nframes_t
  return jacklib.jack_midi_get_lost_event_count(port_buffer)


def jack_free(ptr):
  jacklib.jack_free.argtypes = [c_void_p]
  jacklib.jack_free.restype = None
  return jacklib.jack_free(ptr)

