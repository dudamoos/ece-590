from ctypes import c_double, c_bool, Structure

class BallOffset(Structure):
    _pack_ = 1
    _fields_ = [("err", c_double*2),
	            ("onscreen", c_bool)]

ERR_X = 0
ERR_Y = 1

class ServoPosition(Structure):
	_pack_ = 1
	_fields_ = [("pos", c_double*2)]

POS_X = 0
POS_Y = 1

CAMERA_CHANNEL = "ball-offset"
DYNAMIXEL_CHANNEL = "dxl-position"

