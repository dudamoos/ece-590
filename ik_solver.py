#!/usr/bin/python

from math import pi, cos, sin, atan2, copysign
import numpy as np

# IK functions

def get_dist(p1, p2):
	p1 = np.array(p1, copy=False)
	p2 = np.array(p2, copy=False)
	return np.linalg.norm(p1 - p2)

def get_jacobian(fk, d_theta, theta):
	pose = fk(theta)
	J = np.zeros((len(pose), len(theta)))
	for i in range(len(pose)): # workspace DOF
		for j in range(len(theta)): # robot DOF
			theta_new = np.array(theta)
			theta_new[j] += d_theta
			d_e = fk(theta_new) - pose
			J[i][j] = d_e[i] / d_theta
	return J

# simple path planning - straight line towards goal
def get_next_point_delta(cur, goal, step):
	cur = np.array(cur, copy=False)
	goal = np.array(goal, copy=False)
	m = goal - cur
	m_unit = m / np.linalg.norm(m)
	return step * m_unit

def ik_solve(theta, goal, max_err, theta_step, e_step, fk):
	theta = np.array(theta)
	goal = np.array(goal, copy=False)
	e = fk(theta)
	while (get_dist(e, goal) > max_err):
		J = get_jacobian(fk, theta_step, theta)
		Jp = np.linalg.pinv(J)
		d_e = get_next_point_delta(e, goal, e_step)
		d_theta = Jp.dot(np.transpose([d_e]))
		theta = (theta + np.transpose(d_theta))[0]
		e = fk(theta)
	return theta

# FK functions

def getR(theta):
	"""
	Calculates the composite rotation matrix for the rotation described by
	theta. Each axis rotation becomes a rotation matrix and these are multiplied
	to get the final rotation matrix.

	@param theta - 3x1 vector of rotations about each axis
	@return 3x3 composite rotation matrix
	"""
	Rx = np.array([[1             , 0             , 0],
	               [0             , cos(theta[0]) , -sin(theta[0])],
	               [0             , sin(theta[0]) ,  cos(theta[0])]])
	Ry = np.array([[ cos(theta[1]), 0             ,  sin(theta[1])],
	               [0             , 1             , 0],
	               [-sin(theta[1]), 0             ,  cos(theta[0])]])
	Rz = np.array([[ cos(theta[2]), -sin(theta[2]), 0],
	               [ sin(theta[2]), cos(theta[2]) , 0             ],
	               [0             , 0             , 1             ]])
	return Rx.dot(Ry).dot(Rz)

L1 = 0.24551
L2 = 0.282575
L3 = 0.3127375
L4 = 0.0635
K_LSP = ([0, -0.24551,  0        ], [0, 1, 0])
K_RSP = ([0,  0.24551,  0        ], [0, 1, 0])
K_LSR = ([0,  0      ,  0        ], [1, 0, 0])
K_RSR = ([0,  0      ,  0        ], [1, 0, 0])
K_LSY = ([0,  0      ,  0        ], [0, 0, 1])
K_RSY = ([0,  0      ,  0        ], [0, 0, 1])
K_LEP = ([0,  0      , -0.282575 ], [0, 1, 0])
K_REP = ([0,  0      , -0.282575 ], [0, 1, 0])
K_LWY = ([0,  0      , -0.3127375], [0, 0, 1])
K_RWY = ([0,  0      , -0.3127375], [0, 0, 1])
K_LWR = ([0,  0      ,  0        ], [1, 0, 0])
K_RWR = ([0,  0      ,  0        ], [1, 0, 0])
K_E   = ([0,  0      , -0.0635   ], [0, 0, 0])
T_E   = np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, -0.0635], [0, 0, 0, 1]])

Kleft  = [K_LSP, K_LSR, K_LSY, K_LEP, K_LWY, K_LWR]
Kright = [K_RSP, K_RSR, K_RSY, K_REP, K_RWY, K_RWR]

def getT(theta, pick_lr):
	"""
	@param theta - vector of joint angles in arm
	@param pick_lr - kinematic chain for chosen arm (Kleft or Kright)
	@return 4x4 transformation matrix for end effector relative to base
	"""
	assert len(theta) == len(pick_lr), "joints don't match kinematic model"
	all_T = []

	for entry in zip(theta, pick_lr): # (theta[i], Kin[i] { P, THETA_rot })
		T = np.zeros((4, 4))
		T[3, 3] = 1
		T[0:3:1, 3] = entry[1][0]
		T[0:3:1, 0:3:1] = getR(entry[0] * np.array(entry[1][1]))
		all_T.append(T)

	all_T.append(T_E)
	return reduce(np.dot, all_T) # dot(x, y) does matrix multiplication too

def get_pos(T, coords_to_get="x y z"):
	"""
	@param T - the transformation matrix for the entire set of limbs you
	           are modelling
	@param coords_to_get - a string containing the names of the coords you
	                       want the function to return values for
	@return the requested coords of the end effector modelled by
	"""
	P = T[0:3:1, 3]
	R = T[0:3:1, 0:3:1]
	ret_coords = []

	coords_to_get = coords_to_get.strip().lower()
	if (coords_to_get == ""): coords_to_get = "x y z thx thy thz"
	for coord in coords_to_get.split():
		if coord == "x": ret_coords.append(P[0])
		elif coord == "y": ret_coords.append(P[1])
		elif coord == "z": ret_coords.append(P[2])
		elif coord == "thx": ret_coords.append(atan2(R[2, 1], R[2, 2]))
		elif coord == "thy":
			ret_coords.append(atan2(R[2, 0], R[2,1]**2 + R[2, 2]**2))
		elif coord == "thz": ret_coords.append(atan2(R[1, 0], R[0, 0]))
	return np.array(ret_coords)

def get_fk(theta, pick_lr=Kleft):
	"""
	@param theta - vector of joint angles in arm
	@param pick_lr - kinematic chain for chosen arm (Kleft or Kright)
	@return position in space of the end effector when joints are as theta
	"""
	return get_pos(getT(theta, pick_lr), "x y z")

if __name__ == "__main__":
	max_err = 0.006 # 1% of max radius the 2d arm can reach
	theta_step = 0.01
	e_step = 0.003 # 1/2 of max_err
	theta_start = np.array([0, 0, 0, 0, 0, 0])
	goal = np.array([0, 0.15, 0.2])
	print "Theta start:", theta_start
	print "Pose start:", get_fk(theta_start)
	print "Goal:", goal

	theta_end = ik_solve(theta_start, goal, max_err, theta_step, e_step, get_fk)
	print "Theta end (raw):", theta_end
	print "Pose end (raw):", get_fk(theta_end)
	for i in range(len(theta_end)):
		while (abs(theta_end[i]) > pi):
			theta_end[i] -= copysign(2*pi, theta_end[i])
	e_end = get_fk(theta_end)
	print "Theta end:", theta_end
	print "Pose end:", e_end
	print "Remaining distance:", get_dist(e_end, goal)
	print "Remaining error:", e_end - goal
