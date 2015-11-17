#!/usr/bin/python

import ach
from ctypes import c_double
from time import sleep

chan1 = ach.Channel('example-chan-1')
pos1 = c_double(1)
neg1 = c_double(-1)

chan1.flush()

while True:
	chan1.put(pos1)
	sleep(1)
	chan1.put(neg1)
	sleep(1)

