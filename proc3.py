#!/usr/bin/python

import ach
from ctypes import c_double, Structure
from time import sleep, clock
from sys import argv

L = 5
if (len(argv) >= 2):
	L = int(argv[1])
	print "Using argument L =", L
else:
	print "Using default L =", L

class Proc3Data(Structure):
	_pack_ = 1
	_fields_ = [("val", c_double), ("time", c_double)]

chan2 = ach.Channel('example-chan-2')
chan3 = ach.Channel('example-chan-3')

val2 = c_double()
val3 = Proc3Data()
val3.val = 1.0

chan3.flush()

# wait for initial value
[status, framesize] = chan2.get(val2, wait=True, last=True)
if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES:
	raise ach.AchException(chan2.result_string(status))

while True:
	val3.time = clock()
	val3.val = ((1.0 / val3.val) * (L - 1.0) + val2.value) / L
	chan3.put(val3)
	sleep(1.0 / 50.0)
	
	[status, framesize] = chan2.get(val2, wait=False, last=True)
	if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES:
		raise ach.AchException(chan2.result_string(status))

