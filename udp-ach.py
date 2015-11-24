#!/usr/bin/python

import common
import udp
import struct
import ach

s = udp.UdpSocket(udp.RECV_ADDR, True)

ball_chan = ach.Channel(common.CAMERA_CHANNEL)
off = common.BallOffset()
ball_chan.flush()

while True:
	data = s.recv(udp.EXPECTED_LENGTH)
	if data == None: print "Corructed packet!"
	else:
		x, y, onscreen = struct.unpack(udp.STRUCT_FMT, data)
		print ("Onscreen @", x, y) if onscreen else "Offscreen"
		off.err[common.ERR_X] = x
		off.err[common.ERR_Y] = y
		off.onscreen = onscreen
		ball_chan.put(off)

