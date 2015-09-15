#!/usr/bin/env python

import hubo_ach as ha
import ach
from time import sleep
from math import pi

def joint_diminish(ref, chan_ref, multiplier):
	for j in range(ha.HUBO_JOINT_COUNT):
		ref.ref[j] *= multiplier
	chan_ref.put(ref)
	sleep(1)

chan_state = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
state = ha.HUBO_STATE()

chan_ref = ach.Channel(ha.HUBO_CHAN_REF_NAME)
ref = ha.HUBO_REF()

print "Get current state ..."
[status, framesize] = chan_state.get(state, wait=False, last=True)
for j in range(ha.HUBO_JOINT_COUNT): ref.ref[j] = state.joint[j].pos

print "Reduce by 10% increments ..."
for i in range(5): joint_diminish(ref, chan_ref, 0.9)
print "Reduce by 20% increments ..."
for i in range(5): joint_diminish(ref, chan_ref, 0.8)
print "Reduce by 50% ..."
joint_diminish(ref, chan_ref, 0.5)
print "Set to 0 ..."
joint_diminish(ref, chan_ref, 0)

print "Reset complete ..."

