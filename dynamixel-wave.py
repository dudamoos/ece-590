#!/usr/bin/python

from subprocess import Popen, PIPE
import math
import time

tty_file = '/dev/ttyUSB0'
dev_id = 15

dynamixel = None

try:
	dynamixel = Popen(['./dynamixel-position.py', tty_file], stdin=PIPE)
	time_init = time.time()
	while True:
		time_cur = time.time()
		cur_position = time_cur - time_init
		angle = (math.pi / 2) * math.sin(math.pi * cur_position)
		dynamixel.stdin.write(repr([dev_id, angle]) + '\n')
		time.sleep(time_cur + 0.05 - time.time())
except KeyboardInterrupt:
	if (dynamixel != None): dynamixel.terminate()
