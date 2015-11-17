#!/usr/bin/python

import ach
from ctypes import c_double, Structure
import csv

class Proc3Data(Structure):
	_pack_ = 1
	_fields_ = [("val", c_double), ("time", c_double)]

chan1 = ach.Channel('example-chan-1')
chan2 = ach.Channel('example-chan-2')
chan3 = ach.Channel('example-chan-3')

val1 = c_double()
val2 = c_double()
val3 = Proc3Data()

received_data = []

while True:
	[status, framesize] = chan3.get(val3, wait=True, last=True)
	if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES:
		raise ach.AchException(chan3.result_string(status))
	
	[status, framesize] = chan1.get(val1, wait=False, last=True)
	if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES:
		raise ach.AchException(chan1.result_string(status))
	
	[status, framesize] = chan2.get(val2, wait=False, last=True)
	if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES:
		raise ach.AchException(chan2.result_string(status))
	
	received_data.append([val3.time, val1.value, val2.value, val3.val])
	if ((val3.time % 1.0) <= 0.05):
		print "Tick!"
	
	if (val3.time >= 8.0 + received_data[0][0]):
		print "Exiting!"
		plotter = csv.writer(open('output/output.csv', 'w'))
		plotter.writerow(['time', 'proc1', 'proc2', 'proc3'])
		for row in received_data:
			row_data = [row[0] - received_data[0][0], row[1], row[2], row[3]]
			plotter.writerow(row_data)
		exit(0)

