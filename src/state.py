"""Implementations of the possible states for a robot."""

import time

from matrix import matrix


class BaseState(object):

	def __init__(self, robot):
		self.robot = robot
		self.is_oriented = False  # wut?  states aren't oriented.  robots are.

	def run(self, *args, **kwargs):
		raise NotImplementedError()


class CorridorState(BaseState):
	"""Actions for proceeding down a corridor.

	This algorithm uses proportional-differential control to follow the
	reference trajectory (centerline of the corridor).
	"""

	MOVE_DURATION = 1  # seconds of movement before the next sensor measurement
	SENSOR_ANGLES = {  # commonly-used sensor directions
		'C': 0,	   # shortcut for sensing straight ahead
		'L': 300,  # default angle for sensing to the left
		'R': 60    # default angle for sensing to the right
	}
	TAU_P = 0.2
	TAU_D = 1.0

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


	def run(self, *args, **kwargs):
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
			sensing_side = 'L'
			opposite_side = 'R'
		else:
			sensing_side = 'R'
			opposite_side = 'L'

		# Start the robot
		self.robot.fwd()

		while True:

			# Sense current distance from side of corridor
			dist = self.robot.sense(x=SENSOR_ANGLES[sensing_side])
			ahead_dist = self.robot.sense(x=SENSOR_ANGLES['C'])
			opposite_dist = self.robot.sense(x=SENSOR_ANGLES[opposite_side])

			# Check for dead end
			if (ahead_dist < width) and (dist < width) and (opposite_dist < width):
				print 'Dead end'
				self.robot.rotate(degrees=180)
				self.run(*args, **kwargs)

			# Check for new state
			if (dist > width) or (opposite_dist > width) or (ahead_dist < width):
				print 'End of corridor'
				self.robot.stop()
				break

			# Compute new CTE
			if sensor_side == 'R':
				new_cte = dist - width / 2.0
			else:
				new_cte = width / 2.0 - dist

			# Adjust steering
			steering_factor = -self.TAU_P * new_cte - self.TAU_D * (new_cte - last_cte)
			self.robot.steer(steering_factor)
			last_cte = new_cte

			# Set sensor side to the wall that the robot is steering toward
			if steering_factor > 0:
				pass #sensor_side = 'L'
			else:
				pass #sensor_side = 'R'

			# Pause for delay period:
			time.sleep(self.MOVE_DURATION)

			# Print debug data
			print sensor_side, dist, last_cte, steering_factor
