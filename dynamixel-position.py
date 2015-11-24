#!/usr/bin/python

import serial
import math
import time

import ach
import common

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

dynamixel = serial.Serial('/dev/ttyUSB0', baudrate=1000000)
high_angle = 120.0 * (math.pi/180.0)
low_angle = -120.0 * (math.pi/180.0)

ref_chan = ach.Channel(common.DYNAMIXEL_CHANNEL)
ref = common.ServoPosition()

try:
	while True:
		[status, framesize] = ref_chan.get(ref, wait=True, last=True)
		if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES and status != ach.ACH_MISSED_FRAME:
			raise ach.AchException(ref_chan.result_string())
		
		print "Got position"
		ref.pos[common.POS_X] = min(max(-ref.pos[common.POS_X], low_angle), high_angle)
		ref.pos[common.POS_Y] = min(max(-ref.pos[common.POS_Y], low_angle), high_angle)
		
		set_position(dynamixel, 3, ref.pos[common.POS_X])
		set_position(dynamixel, 2, ref.pos[common.POS_Y])
except KeyboardInterrupt:
	dynamixel.close()
except:
	dynamixel.close()
	raise

