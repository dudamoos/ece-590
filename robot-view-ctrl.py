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
import diff_drive
import ach
import sys
import time
from ctypes import *
import cv2.cv as cv
import cv2
import numpy as np

ref = diff_drive.H_REF()
tim = diff_drive.H_TIME()

ROBOT_DIFF_DRIVE_CHAN   = 'robot-diff-drive'
ROBOT_CHAN_VIEW   = 'robot-vid-chan'
ROBOT_TIME_CHAN  = 'robot-time'
# CV setup 
cv.NamedWindow("wctrl", cv.CV_WINDOW_AUTOSIZE)

# added
nx = 320
ny = 240

r = ach.Channel(ROBOT_DIFF_DRIVE_CHAN)
r.flush()
v = ach.Channel(ROBOT_CHAN_VIEW)
v.flush()
t = ach.Channel(ROBOT_TIME_CHAN)
t.flush()


print '======================================'
print '============= Robot-View ============='
print '========== Daniel M. Lofaro =========='
print '========= dan@danLofaro.com =========='
print '======================================'
while True:
    # Get Frame
    img = np.empty((ny,nx,3), np.uint8)
    [status, framesize] = v.get(img, wait=False, last=True)
    if (status != ach.ACH_OK) and (status != ach.ACH_MISSED_FRAME) and (status != ach.ACH_STALE_FRAMES):
        raise ach.AchException( v.result_string(status) )
    img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    
#    [status, framesize] = t.get(tim, wait=False, last=True)
#    if (status != ach.ACH_OK) and (status != ach.ACH_MISSED_FRAME) and (status != ach.ACH_STALE_FRAMES):
#        raise ach.AchException( t.result_string(status) )

#-----------------------------------------------------
#--------[ Do not edit above ]------------------------
#-----------------------------------------------------
    # Def:
    # ref.ref[0] = Right Wheel Velos
    # ref.ref[1] = Left Wheel Velos
    # tim.sim[0] = Sim Time
    # img        = cv image in BGR format
    
    ref.ref[0] = 0.5 #0.1 #0.5
    ref.ref[1] = -0.5 #-0.1 #-0.5
    
    green_x = 0
    green_y = 0
    green_c = 0
    
    for y in range(ny):
        for x in range(nx):
            [p_b, p_g, p_r] = img[y][x]
            if ((p_g > 2*p_r) and (p_g > 2*p_b)):
                green_x += x
                green_y += y
                green_c += 1
    
    pos_string = "offscreen"
    if (green_c > 0):
    	green_x /= green_c
    	green_y /= green_c
    	for y in range(max(green_y-2, 0), min(green_y+3, ny)):
    	    for x in range(max(green_x-2, 0), min(green_x+3, nx)):
    	        img[y][x] = [0x00, 0x00, 0xFF]
    	green_x = green_x - nx/2
    	green_y = -(green_y - ny/2)
    	pos_string = str((green_x, green_y))
    
    print 'Sim Time =', tim.sim[0], ' \tPosition =', pos_string
    cv2.imshow("wctrl", img)
    cv2.waitKey(10)
    
    # Sets reference to robot
    r.put(ref);

    # Sleeps
    time.sleep(0.1)   
#-----------------------------------------------------
#--------[ Do not edit below ]------------------------
#-----------------------------------------------------
