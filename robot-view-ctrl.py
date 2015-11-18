#!/usr/bin/python -OO
# /* -*-  indent-tabs-mode:t; tab-width: 8; c-basic-offset: 8  -*- */
# /*
# Copyright (c) 2014, Daniel M. Lofaro <dan (at) danLofaro (dot) com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# */
import time
import cv2.cv as cv
import cv2
import numpy as np

HSV_MAX = np.array((120 + 30, 255, 255), np.uint8)
HSV_MIN = np.array((120 - 30,  50,   0), np.uint8)
MARK_RED = cv.Scalar(0x00, 0x00, 0xFF)
IMG_W = 320
IMG_H = 240

# CV setup 
cv.NamedWindow("webcam", cv.CV_WINDOW_AUTOSIZE)
cv.NamedWindow("detect", cv.CV_WINDOW_AUTOSIZE)
capture = cv2.VideoCapture(0)

while True:
    # Get Frame
    ret, frame = capture.read()
    frame = cv2.resize(frame, (IMG_W, IMG_H))
    detect = cv2.cvtColor(frame, cv.CV_BGR2HSV)
    detect = cv2.inRange(detect, HSV_MIN, HSV_MAX)
    
    [ys, xs] = detect.nonzero()
    if (len(ys) > 0):
        x = xs.mean()
        y = ys.mean()
        cv2.rectangle(frame, (int(x)-2, int(y)-2), (int(x)+3, int(y)+3), MARK_RED, cv.CV_FILLED)
        x = x / (IMG_W / 2.0) - 1.0
        y = -y / (IMG_H / 2.0) + 1.0
        print "Offset Ratio: ", x, y
    else:
        print "Ball Offscreen"
    
    cv2.imshow("webcam", frame)
    cv2.imshow("detect", detect)
    cv2.waitKey(10)

    # Sleeps
    time.sleep(0.1)
