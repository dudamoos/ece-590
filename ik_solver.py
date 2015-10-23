#!/usr/bin/python

import math
import numpy as np

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

# specific 2D arm from class
FK_2D_LIMBS = [0.3, 0.2, 0.1]
def get_fk_2d(theta):
	assert len(theta) == len(FK_2D_LIMBS)
	x_comps = [FK_2D_LIMBS[i] * math.cos(sum(theta[0:(i + 1)])) for i in range(len(FK_2D_LIMBS))]
	y_comps = [FK_2D_LIMBS[i] * math.sin(sum(theta[0:(i + 1)])) for i in range(len(FK_2D_LIMBS))]
	return np.array([sum(x_comps), sum(y_comps)])

if __name__ == "__main__":
	max_err = 0.006 # 1% of max radius the 2d arm can reach
	theta_step = 0.01
	e_step = 0.003 # 1/2 of max_err
	theta_start = np.array([0, 0, 0])
	goal = np.array([0, 0.15])
	print "Theta start:", theta_start
	print "Pose start:", get_fk_2d(theta_start)
	print "Goal:", goal
	
	theta_end = ik_solve(theta_start, goal, max_err, theta_step, e_step, get_fk_2d)
	for i in range(len(theta_end)):
		while (abs(theta_end[i]) > math.pi):
			theta_end[i] -= math.copysign(2*math.pi, theta_end[i])
	e_end = get_fk_2d(theta_end)
	print "Theta end:", theta_end
	print "Pose end:", e_end
	print "Remaining distance:", get_dist(e_end, goal)
	print "Remaining error:", e_end - goal
