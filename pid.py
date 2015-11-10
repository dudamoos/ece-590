import numpy as np

class PController:
	def __init__(self, target, Kp, bound):
		self.target = target
		self.Kp = Kp
		self.bound = bound
	
	def control(self, distance, cur_time):
		# proportional error
		p_error = distance - self.target
		# output
		ctl = self.Kp*p_error
		# output limiter
		ctl = min(max(ctl, -self.bound), self.bound)
		# debug
		print "Dist = % 3.4f, Ep = % 3.4f, C = % 3.4f" % (distance, p_error, ctl)
		return ctl

class PidController:
	def __init__(self, target, Kp, Ki, Kd, bound, cur_time, window_size):
		# controller parameters
		self.target = target
		self.Kp = Kp
		self.Ki = Ki
		self.Kd = Kd
		self.bound = bound
		# controller state
		self.last_time = cur_time
		self.window = np.zeros((2, window_size))
	
	def control(self, distance, cur_time):
		dt = float(cur_time - self.last_time)
		# proportional error
		p_error = distance - self.target
		# integral error
		i_error = self.window.prod(0).sum() + p_error * dt
		# derivative error
		d_error = (p_error - self.window[0,0]) / dt
		# output
		ctl = self.Kp*p_error + self.Kd*d_error + self.Ki*i_error
		# output limiter
		ctl = min(max(ctl, -self.bound), self.bound)
		
		# feedback
		self.last_time = cur_time
		self.window = np.roll(self.window, 1)
		self.window[0,0] = p_error
		self.window[0,1] = dt
		
		# debug
		print("Dist = % 3.4f, Ep = % 3.4f, Ei = % 3.4f, Ed = % 3.4f, C = % 3.4f"
			% (distance, p_error, i_error, d_error, ctl))
		
		return ctl
		
