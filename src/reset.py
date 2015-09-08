#!/usr/bin/env python

import hubo_ach as ha
import ach
from time import sleep
from math import pi

chan_ref = ach.Channel(ha.HUBO_CHAN_REF_NAME)
ref = ha.HUBO_REF()

print "Start reset ..."

# Reset wrist and hand, but not shoulder yet
ref.ref[ha.LEB] = -pi / 2
ref.ref[ha.LSP] = -pi / 2
ref.ref[ha.LWY] = 0
ref.ref[ha.LF1] = 0
ref.ref[ha.LF2] = 0
ref.ref[ha.LWP] = 0
chan_ref.put(ref)
sleep(2)

# Slowly lower arm
for i in range(10):
	ref.ref[ha.LEB] += pi / 20
	ref.ref[ha.LSP] += pi / 20
	chan_ref.put(ref)
	sleep(1)
	
print "Reset complete ..."

