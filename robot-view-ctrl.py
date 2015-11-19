#!/usr/bin/python -OO

#import time
import cv2.cv as cv
import cv2
import numpy as np

import ach
import common

HSV_MAX = np.array((120 + 30, 255, 255), np.uint8)
HSV_MIN = np.array((120 - 30,  50,   0), np.uint8)
IMG_W = 320
IMG_H = 240

# CV setup 
cv.NamedWindow("detect", cv.CV_WINDOW_AUTOSIZE)
capture = cv2.VideoCapture(0)

ball_chan = ach.Channel(common.CAMERA_CHANNEL)
off = common.BallOffset()
ball_chan.flush()

while True:
	# Get Frame
	ret, frame = capture.read()
	frame = cv2.resize(frame, (IMG_W, IMG_H))
	frame = cv2.cvtColor(frame, cv.CV_BGR2HSV)
	frame = cv2.inRange(frame, HSV_MIN, HSV_MAX)
	
	[ys, xs] = frame.nonzero()
	if (len(ys) > 0):
		off.onscreen = True
		x = xs.mean()
		y = ys.mean()
		cv2.rectangle(frame, (int(x)-2, int(y)-2), (int(x)+3, int(y)+3), 0x7F, cv.CV_FILLED)
		off.err[common.POS_X] = x / (IMG_W / 2.0) - 1.0
		off.err[common.POS_Y] = -y / (IMG_H / 2.0) + 1.0
	else:
		off.onscreen = False
	ball_chan.put(off)
    
	cv2.imshow("detect", frame)
	cv2.waitKey(10)

	# Sleeps
	#time.sleep(0.1)
