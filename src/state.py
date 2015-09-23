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
	"""Actions for proceeding down a corridor.

	This algorithm uses proportional-differential control to follow the
	reference trajectory (centerline of the corridor).
	"""

	MOVE_DURATION = 2  # seconds of movement before the next sensor measurement
	SENSOR_ANGLES = {
		'L': 300,  # default angle for sensing to the left
		'R': 60    # default angle for sensing to the right
	}
	TAU_P = 0.1
	TAU_D = 0.5

	def _sense_initial_position(self):
		"""Learn about this corridor and our place in it.

		Returns a tuple (x, y), where:
			x is the total width of the corridor in cm.
			y is the displacement from the corridor center in cm.  Positive
				displacement indicates a position left of center.
		"""

		right_dist = self.robot.sense(x=90)
		left_dist = self.robot.sense(x=270)
		width = right_dist + left_dist

		return (width / 2.0 - left_dist, width)


	def run(self, callback, *args, **kwargs):
		print 'Running CorridorState'

		# Ensure the robot is stopped
		self.robot.stop()

		# TODO: orient the robot, if is_oriented is False.
		# Until then, assume the robot is centered and aligned on the corridor.
		self.is_oriented = True

		# Sense the cross-track error and width of the corridor:
		last_cte, width = self._sense_initial_position()
		print 'Corridor width: {0}'.format(width)
		if last_cte > 0:
			sensor_side = 'R'
		else:
			sensor_side = 'L'

		# Start the robot
		self.robot.fwd()

		# True when a new (non-corridor) state is detected
		new_state = False

		while not new_state:

			# Sense new cte
			angle = SENSOR_ANGLES[sensor_side]
			dist = self.robot.sense(x=angle)
			if sensor_side == 'R':
				new_cte = dist - width
			else:
				new_cte = width - dist

			# Check for new state
			# TODO: sense logic for state change detection

			# Adjust steering
			steering_factor = -TAU_P * new_cte - TAU_D * (new_cte - last_cte)
			self.robot.steer(steering_factor)
			last_cte = new_cte

			# Pause for delay period:
			time.sleep(MOVE_DURATION)

			# Print debug data
			print sensor_side, dist, last_cte, steering_factor
