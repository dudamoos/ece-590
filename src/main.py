#!/usr/bin/python

import hubo_ach as ha
import ach
from time import sleep
import math

# Constants
LEG_UPPER = 300.3
LEG_LOWER = 300.38
LEG_TOTAL = LEG_UPPER + LEG_LOWER
HIP_TO_MID = 88.43

H_TOP = math.sqrt(LEG_TOTAL**2 - HIP_TO_MID**2)
H_MID = H_TOP - 200
L_H_MID = H_TOP/2 + 50
L_AMP = H_TOP/2 - 50

REF_INTERVAL = 0.05

def debug_joint(name, index, ref, state):
	if (abs(ref.ref[index] - state.joint[index].pos) > 0.15):
		print "{0} is slipping! -> ref {1:3.4f}\tstate {2:3.4f}".format(name, ref.ref[index], state.joint[index].pos)

def run_phase(ref, chan_ref, state, chan_state, phase_func, phase_length):
	[status, framesize] = chan_state.get(state, wait=False, last=True)
	time_init = state.time
	time_last = time_init + phase_length
	while True:
		# Adaptive delay (timing)
		[status, framesize] = chan_state.get(state, wait=False, last=True)
		time_cur = state.time
		# Debug
		debug_joint("RHP", ha.RHP, ref, state)
		debug_joint("RKP", ha.RKN, ref, state)
		debug_joint("RAP", ha.RAP, ref, state)
		# Phase time (emulate do-while)
		if (time_cur >= time_last): break
		# Step calculations
		phase_func(ref, time_cur - time_init)
		chan_ref.put(ref)
		# Adaptive delay (sleep)
		[status, framesize] = chan_state.get(state, wait=False, last=True)
		sleep(time_cur + REF_INTERVAL - state.time)
	# Ensure phase reaches its final point
	phase_func(ref, phase_length)
	chan_ref.put(ref)
	sleep(0.5) # aribitrary inter-phase delay

# Robot lifts its arms over 1 second
def arm_phase(ref, phase_time):
	# IK
	gamma = (math.pi / 6)*(1 - math.cos(math.pi * phase_time))
	# Ref output
	ref.ref[ha.RSR] = -gamma
	ref.ref[ha.LSR] = gamma

# Robot eases into new support polygon over 2 seconds
def lean_phase(ref, phase_time):
	# IK
	w = (HIP_TO_MID/2)*(1 - math.cos((math.pi / 2) * phase_time))
	theta = math.asin(w / LEG_TOTAL)
	# Ref output
	ref.ref[ha.RHR] = ref.ref[ha.LHR] = theta
	ref.ref[ha.RAR] = ref.ref[ha.LAR] = -theta

# Robot lifts its left leg over 2 seconds
def lift_phase(ref, phase_time):
	# IK
	l = L_AMP*math.cos((math.pi / 2) * phase_time) + L_H_MID
	phi = math.acos(( LEG_UPPER**2 + LEG_LOWER**2 - l**2) / (2*LEG_UPPER*LEG_LOWER))
	a   = math.acos(( LEG_UPPER**2 - LEG_LOWER**2 + l**2) / (2*LEG_UPPER*l))
	b   = math.acos((-LEG_UPPER**2 + LEG_LOWER**2 + l**2) / (2*LEG_LOWER*l))
	psi = math.pi - phi
	# Ref output
	ref.ref[ha.LHP] = -a
	ref.ref[ha.LKN] = psi
	ref.ref[ha.LAP] = -b

def acos_clamped(ratio): return math.acos(max(min(ratio, 1.0), -1.0))
# Robot moves up and down with a period of 4 seconds
def hop_phase(ref, phase_time):
	# IK
	h = 200*math.cos((math.pi / 2) * phase_time) + H_MID
	l = math.sqrt(h**2 + HIP_TO_MID**2)
	theta = math.atan(HIP_TO_MID / h)
	phi = acos_clamped(( LEG_UPPER**2 + LEG_LOWER**2 - l**2) / (2*LEG_UPPER*LEG_LOWER))
	a   = acos_clamped(( LEG_UPPER**2 - LEG_LOWER**2 + l**2) / (2*LEG_UPPER*l))
	b   = acos_clamped((-LEG_UPPER**2 + LEG_LOWER**2 + l**2) / (2*LEG_LOWER*l))
	psi = math.pi - phi
	# Ref output
	ref.ref[ha.RHR] = ref.ref[ha.LHR] = theta
	ref.ref[ha.RAR] = -theta
	ref.ref[ha.LAR] = 0
	ref.ref[ha.RHP] = -a
	ref.ref[ha.RKN] = psi
	ref.ref[ha.RAP] = -b

# Open Hubo-Ach feed-forward and feed-back (reference and state) channels
chan_state = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
chan_ref = ach.Channel(ha.HUBO_CHAN_REF_NAME)

# Variables to hold state and reference
state = ha.HUBO_STATE()
ref = ha.HUBO_REF()

# Run the program
print "Lifting arms ..."
run_phase(ref, chan_ref, state, chan_state, arm_phase, 1)
print "Leaning ..."
run_phase(ref, chan_ref, state, chan_state, lean_phase, 2)
print "Lifting foot ..."
run_phase(ref, chan_ref, state, chan_state, lift_phase, 2)
print "Hopping ..."
run_phase(ref, chan_ref, state, chan_state, hop_phase, 25)

# Return the robot to normal
import reset

