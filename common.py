from ctypes import c_double, c_bool, Structure

class PT_STATE(Structure):   # for 
	_pack_ = 1
	_fields_ = [("pos", c_double*2),  # position of servos
	            ("time", c_double)]   # time

class BallOffset(Structure): # for the camera backends
    _pack_ = 1
    _fields_ = [("err", c_double*2),  # ball offset from camera
	            ("onscreen", c_bool)] # ball onscreen

class PT_REF(Structure):
	_pack_ = 1
	_fields_ = [("pos", c_double*2)]  # commanded servo position

ERR_X = 0
ERR_Y = 1

POS_X = 0
POS_Y = 1

CAMERA_CHANNEL = "ball-offset"
STATE_CHANNEL = "pt-state"
REF_CHANNEL = "pt-ref"

