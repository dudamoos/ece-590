#!/usr/bin/python

import ach
from ctypes import c_double
from time import sleep

chan1 = ach.Channel('example-chan-1')
chan2 = ach.Channel('example-chan-2')

val1 = c_double()
val2 = c_double()

chan2.flush()

while True:
	[status, framesize] = chan1.get(val1, wait=True, last=True)
	if status == ach.ACH_OK or status == ach.ACH_STALE_FRAMES:
		val2.value = val1.value * 2.5
		chan2.put(val2)
	else:
		raise ach.AchException(chan1.result_string(status))

