"""Implementations of the possible states for a robot."""

import sys
import time

from matrix import matrix

import numpy


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

	DEGREES_FROM_STRAIGHT = range(180, -180, -10)
	RELATIVE_ANGLES = [d % 360 for d in range(270, 460, 10)]
	MOVE_DURATION = 1  # seconds of movement before the next sensor measurement
	SENSOR_ANGLES = {  # commonly-used sensor directions
		'L': 300,  # default angle for sensing to the left
		'R': 60    # default angle for sensing to the right
	}
	TAU_P = 0.2
	TAU_D = 1.0

	# Probability distribution for the direction of the corridor relative to
	# the heading of the robot.  The distribution covers a 360-degree arc in
	# 10-degree increments. Initialized as a uniform distribution (heading
	# unknown).
	# TODO: should p_heading be an attribute on the robot rather than on state?
	p_heading = [1.0 / (360 / 10)] * (360 / 10)

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

	def _find_perpendicular(self, measurements, recur=True):
		"""Find the index of the perpendicular measurement.

		Args:
		measurements - a list of distance measurements across a continuous arc.
		recur - if False, do not recur again, as this is already the second
			attempt with this measurement set.

		Returns the index of the perpendicular measurement.  This function uses
		a hill-climb algorithm to find the center of the "dip" in measurement
		values, which will indicate the measurement taken perpendicular to an
		obstacle.
		"""

		for m in sorted(set(measurements)):
			left_bound = None
			right_bound = None
			i = measurements.index(m)
			if i == 0:
				continue  # can't rely on extreme left or right measurements
			try:
				if measurements[i - 1] < m or measurements[i + 1] < m:
					continue  # we're on a slope, not a min
				for j in range(1, len(measurements)):
					if measurements[i - j] > m:
						left_bound = left_bound or i - j
					if measurements[i + j] > m:
						right_bound = right_bound or i + j
					if (left_bound is not None) and (right_bound is not None):
						return left_bound + (right_bound - left_bound) / 2
			except IndexError:
				continue

		if recur:
			measurements.reverse()
			i = self._find_perpendicular(measurements, recur=False)
			return len(measurements) - 1 - i
		else:
			# At this point, the mins are at both ends of measurements, which
			# means perpendicular is the first (and last) measurement.
			return 0

	def _orient(self):
		self.robot.stop()
		self.p_heading = self._find_p_heading()
		turn_angle = self._turn_down_corridor()
		self.p_heading = self._rotate_p_heading(turn_angle)

	def _find_p_heading(self):
		"""Use a full sweep of sensor measurements to populate p_heading."""
		angles = [a % 360 for a in range(270, 460, 10)]
		measurements = []
		for angle in angles:
			measurements.append(self.robot.dist(angle))

		index_of_perpendicular = self._find_perpendicular(measurements)
		index_of_perpendicular += 9  # 180 deg measurements vs 360 deg headings

		# TODO: expose azimuth error through the mount, and generate the
		# error histogram from that.
		p_heading = [0] * 36
		p_heading[index_of_perpendicular] = 0.6
		try:
			p_heading[index_of_perpendicular + 1] = 0.2
			p_heading[index_of_perpendicular - 1] = 0.2
		except IndexError:
			pass

		print p_heading
		return p_heading

	def _turn_down_corridor(self):
		turn_angle = numpy.random.choice(self.DEGREES_FROM_STRAIGHT,
										 p=self.p_heading)
		print 'Rotating {0}'.format(turn_angle)
		self.robot.rotate(turn_angle)

		return turn_angle

	def _rotate_p_heading(self, degrees=0):
		"""Adjust the expected direction of the corridor after a turn.

		Args:
		degrees - the magnitude of the adjustment.  Adjust to the left for
			positive values, and to the right for negative values.

		Returns the new p_heading.
		"""

		steps = degrees / 10

		return [
			self.p_heading[(i + steps) % 36] for i in range(len(self.p_heading))
		]

	def run(self, *args, **kwargs):
		print 'Running CorridorState'

		# Ensure the robot is stopped
		self.robot.stop()

		if not self.is_oriented:
			self.is_oriented = self._orient()
			print self.p_heading
			sys.exit()

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
			dist = self.robot.sense(x=self.SENSOR_ANGLES[sensing_side])

			# Check for new state
			if dist > width:
				print 'End of corridor'
				self.robot.stop()
				break

			# Compute new CTE
			if sensing_side == 'R':
				new_cte = dist - width / 2.0
			else:
				new_cte = width / 2.0 - dist

			# Adjust steering
			steering_factor = -self.TAU_P * new_cte - self.TAU_D * (new_cte - last_cte)
			self.robot.steer(steering_factor)
			last_cte = new_cte

			# Pause for delay period:
			time.sleep(self.MOVE_DURATION)

			# Print debug data
			print sensing_side, dist, last_cte, steering_factor
