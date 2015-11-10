import numpy as np
import cv2

SCREEN_WIDTH = 320
TRUE_RADIUS = 0.5

CAMERA_FOV = 1.047
FOCAL_LENGTH = 0.085
BASELINE = 0.4
PIXEL_SIZE = 280.0e-6

COLOR_MAX = np.array((0x80, 0xFF, 0xFF), np.uint8)
COLOR_MIN = np.array((0x00, 0x20, 0x20), np.uint8)

def find_ball(img):
	xs = cv2.inRange(img, COLOR_MIN, COLOR_MAX).nonzero()[0]
	return (xs.mean(), len(xs))

def get_stereo_distance(imgL, imgR):
	l_x, area = find_ball(imgL)
	if (area == 0): return (np.nan, -1.0)
	r_x, area = find_ball(imgR)
	if (area == 0): return (np.nan, -1.0)
	d_x = abs(r_x - l_x)
	dist = (FOCAL_LENGTH * BASELINE) / (d_x * PIXEL_SIZE)
	x = (l_x + r_x) / 2
	return (x, dist)

def get_mono_distance(img):
	x, area = find_ball(img)
	if (area == 0): return (np.nan, -1.0)
	radius = np.sqrt(area / np.pi)
	subtended = radius / SCREEN_WIDTH * CAMERA_FOV
	dist = TRUE_RADIUS / np.tan(subtended)
	return (x, dist)

