#!/usr/bin/python

# Code by Layanne Hazim

import common
import ach
from time import time, sleep
from math import pi

Input = ach.Channel(common.CAMERA_CHANNEL)
Output = ach.Channel(common.DYNAMIXEL_CHANNEL)
err = common.BallOffset()
ServoPosition = common.ServoPosition()

#-pi/4 to pi/4

Kp = pi/4
Kd = 0.01
#Ki = 
freq = 50.0
period = 1/freq
err_0 = [0.0, 0.0]
err_i0 = [err_0[0]*period, err_0[1]*period]
pos_0 = [0.0, 0.0]

#xy: 0 for x 
#xy: 1 for y

def PID(err, xy):
	theta_rp = err*Kp
	theta_rpd = theta_rp + Kd*(err-err_0[xy])/period
	#err_i1 = err*period
	#theta_rpid = theta_rpd + Ki*(err_i0[xy] + err_i1)
	#err_i0[xy] += ei1
	#err_0[xy] = err
	return theta_rpd#id

def vel2pos(velos, xy):
	return pos_0[xy] + velos*period

ServoPosition.pos[common.POS_X] = 0.0
ServoPosition.pos[common.POS_Y] = 0.0
Output.put(ServoPosition)

i = 0

while(True):
	i += 1
	startTime = time() 
	[status, framesize] = Input.get(err, wait=False, last=True)
	if status != ach.ACH_OK and status != ach.ACH_STALE_FRAMES and status != ach.ACH_MISSED_FRAME:
		raise ach.AchException(Input.result_string())
	
	if(err.onscreen):
		pos_x = vel2pos(PID(err.err[common.ERR_X], 0), 0)
		pos_y = vel2pos(PID(err.err[common.ERR_Y], 1), 1)
		pos_0 = [pos_x, pos_y]
	else:
		pos_x = vel2pos(0.5,0) if abs((i % 320) - 160) < 80 else vel2pos(-0.5,0)
		pos_y = 0 #vel2pos(0.5,1) if abs((i % 320) - 160) < 80 else vel2pos(-0.5,1)
		pos_0 = [pos_x, pos_y]
	
	ServoPosition.pos[common.POS_X] = pos_0[0]
	ServoPosition.pos[common.POS_Y] = pos_0[1]
	Output.put(ServoPosition)
	
	timeTaken = startTime + period - time()
	if (timeTaken > 0):
		sleep(timeTaken)

