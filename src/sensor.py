"""Implementations for available sensors."""


def median(x):
	"""Return the median of a list of values."""

	m, r = divmod(len(x), 2)
	if r:
		return sorted(x)[m]
	return sum(sorted(x)[m - 1:m + 1]) / 2


class UltrasonicSensor(object):

	def __init__(self, driver=None, mount=None, pin=15):
		self.driver = driver
		self.mount = mount
		self.pin = pin

	def sense_distance(self, angle):
		"""Sense the distance at a given direction.

		Args:
		angle - the direction to sense, where 0 is straight ahead.  Must be in
			the forward arc of the robot (270 degrees clockwise to 90 degrees).

		Returns distance in cm.  The sensor is commanded to take three
		measurements, and the median measurement is returned.
		"""

		self.mount.swivel(angle)

		measurements = []
		for i in range(3):
			measurements.append(self.driver.us_dist(self.pin))

		return median(measurements)

	def sense_swath(self, angle):
		"""Sense the distance at a given general direction.

		Args:
		angle - the center of the swath to measure, where 0 is straight ahead.

		Returns distance in cm.  Measurements are taken at the given angle, and
			at +/- 15 degrees from that angle, for a 30-degree swath. The
			smallest distance is returned.
		"""

		measurements = []
		for a in range(angle - 15, angle + 30, 15):
			measurements.append(self.sense_distance(a))

		return min(measurements)