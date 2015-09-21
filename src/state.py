"""Implementations of the possible states for a robot."""

import time

from matrix import matrix


class BaseState(object):

	def __init__(self, robot):
		self.robot = robot
		self.is_oriented = False  # wut?  states aren't oriented.  robots are.

	def run(self, callback, *args, **kwargs):
		raise NotImplementedError()


class CorridorState(BaseState):

	MOVE_DURATION = 2  # seconds of movement before the next sensor measurement
	SERVO_DELAY = 0.5  # seconds of time to allow servo to complete movement


	def _sense_initial_position(self):
		"""Learn about this corridor and our place in it."""
		self.robot.driver.servo(0)
		time.sleep(SERVO_DELAY)
		right_dist = self.robot.driver.us_dist(robot.SENSOR_PIN)
		# TODO: do we need a SENSOR_DELAY?

		self.robot.driver.servo(180)
		time.sleep(SERVO_DELAY)
		left_dist = self.robot.driver.us_dist(robot.SENSOR_PIN)

		if left_dist < right_dist:
			return 'L', left_dist, left_dist + right_dist
		else:
			return 'R', right_dist, left_dist + right_dist


	def run(self, callback, *args, **kwargs):
		# Ensure the robot is stopped
		self.robot.driver.stop()

		# TODO: orient the robot, if is_oriented is False.
		# Until then, assume the robot is centered and aligned on the corridor.
		self.is_oriented = True

		# Sense the initial position:
		# Detect the distance and direction (L/R) to the nearest wall:
		closest_side, dist, width = self._sense_initial_position()

		# Initialize the robot's position/velocity state "x", expressed as:
		# [0] distance in cm from the nearest side
		# [1] lateral velocity (toward or away from the side) in cm/sec
		x = matrix([[dist], [0.]])

		# Initial uncertainty:
		# TODO: add measurement uncertainty at [0][0]
		P = matrix([[0., 0.], [0., 0.]])

		# external motion (none modeled)
		u = matrix([[0.], [0.]])

		# Next state function:
		# [0][1] = 1 -> apply full velocity to position
		F = matrix([[1., 1.], [0, 1.]])

		# Measurement function (extracts the position element from x)
		H = matrix([[1., 0.]])

		# Measurement uncertainty (none modeled)
		R = matrix([[1.]])

		# Identity matrix (matrix equivalent of 1)
		I = matrix([[1., 0.], [0., 1.]])

		while True:

			# 1. Are we in a state transition condition?
			# If so, set new state and break.

			# 2. Move
			# Start the robot, if not already moving
			self.robot.driver.fwd()

			# Pause for delay period:
			time.sleep(MOVE_DURATION)

			# Apply motion update prediction to state vector
	        x = (F * x) + u
	        P = F * P * F.transpose()

	        # 3. Sense
	        # Take a sensor measurement
	        # robot.sense()

	        # Have we reached a new state?
	        # If so, stop the robot and break
	        if False:  # detect new state here
		        robot.driver.stop()
		        # TODO: change robot's state attribute
		        # break

	        # Apply measurement update to state vector
	        # Z = matrix([measurements[n]])
	        # y = Z.transpose() - (H * x)
	        # S = H * P * H.transpose() + R
	        # K = P * H.transpose() * S.inverse()
	        # x = x + (K * y)
	        # P = (I - (K * H)) * P

	        # 4. Is an adjustment needed?
	        # If so, turn the robot
	        # robot.turn(degrees, current_speed)

			pass
