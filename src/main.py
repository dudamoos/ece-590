#!/usr/bin/env python

import hubo_ach as ha
import ach
import sys
import time
import math
from ctypes import *

# Open Hubo-Ach feed-forward and feed-back (reference and state) channels
chan_state = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
chan_ref = ach.Channel(ha.HUBO_CHAN_REF_NAME)

# Variables to hold state and reference
state = ha.HUBO_STATE()
ref = ha.HUBO_REF()

# Move arm into position
ref.ref[ha.LEB] = -math.pi / 2
ref.ref[ha.LSP] = -math.pi / 2
ref.ref[ha.LWY] = math.pi / 2
ref.ref[ha.LF1] = math.pi / 2
ref.ref[ha.LF2] = math.pi / 2
chan_ref.put(ref)
# Allow the robot time to stabilize
time.sleep(5)

wave_rot = math.pi / 3
while True:
	# Display the current state
	[statuses, framesizes] = chan_state.get(state, wait=False, last=False)
	print "LWP:", state.joint[ha.LWP].pos
	# Set the new state
	ref.ref[ha.LWP] = wave_rot
	wave_rot = -wave_rot
	chan_ref.put(ref)
	# Wait for the next frame
	time.sleep(0.5)

