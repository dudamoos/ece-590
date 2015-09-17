#!/usr/bin/python

import serial
import math
import time

def rad2tick(r):
	r += 150 * math.pi / 180.0
	ticks = r * 0x3ff / (300 * math.pi / 180.0)
	return int(math.floor(ticks))

def tick2rad(ticks):
	r = ticks * (300 * math.pi / 180.0) / 1023.0
	r -= 150 * math.pi / 180.0
	return r

def write_register(ser, dev_id, address, value):
	value_l = value & 0xff
	value_h = (value & 0xff00) >> 8
	# ID, length, instruction, address, value_l, value_h, cksum
	# length is byte count of instruction + payload + cksum
	# WRITE_DATA instruction id 0x03
	data = [dev_id, 5, 0x03, address, value_l, value_h]
	checksum = ~reduce(lambda x,y: x+y, data) & 0xff
	packet = b'\xff\xff' + bytearray(data) + bytearray([checksum])
	ser.write(packet)

def set_position(ser, dev_id, angle):
	# Goal Position is a 16-bit, little-endian number at address 0x1e
	write_register(ser, dev_id, 0x1e, rad2tick(angle))

dynamixel = serial.Serial("/dev/ttyUSB0", baudrate=1000000)
dev_id = 15 # TODO: grab from args

try:
	time_init = time.time()
	while True:
		time_cur = time.time()
		cur_position = time_cur - time_init
		angle = (math.pi / 2) * math.sin(math.pi * cur_position)
		set_position(dynamixel, dev_id, angle)
		time.sleep(time_cur + 0.05 - time.time())
except KeyboardInterrupt:
	dynamixel.close()

