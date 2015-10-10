"""Implementations for available sensors."""

DEFAULT_PIN = 15


def median(x):
	"""Return the median of a list of values."""

	m, r = divmod(len(x), 2)
	if r:
		return sorted(x)[m]
	return sum(sorted(x)[m - 1:m + 1]) / 2


class BaseSensor(object):
	"""An abstract base class for sensors."""

	def __init__(self, driver=None, mount=None, pin=DEFAULT_PIN,
				 error_fnc=lambda x: x):
		"""Initialize the sensor.

		Args:
		driver - a module that exposes the functions used by the sensor.
		mount - a Mount instance to support sensor movement.  If None, the
			sensor is fixed (non-moveable).
		pin - the controller board pin that the sensor is connected to.
		error_fnc - a function that corrects a sensor reading for error
			(default no error).
		"""

		self.driver = driver
		self.mount = mount
		self.pin = pin
		self.error_fnc = error_fnc

	def sense(self, *args, **kwargs):
		raise NotImplementedError

	def center(self):
		if not self.mount:
			raise ValueError('center commanded to fixed sensor')
		self.mount.center()


class UltrasonicSensor(BaseSensor):

	def sense(self, *args, **kwargs):
		return self.sense_swath(kwargs['x'])

	def sense_distance(self, angle):
		"""Sense the distance at a given direction.

		Args:
		angle - the direction to sense, where 0 is straight ahead.  Must be in
			the forward arc of the robot (270 degrees clockwise to 90 degrees).

		Returns distance in cm.  The sensor is commanded to take three
		measurements, and the median measurement is returned.
		"""

		if angle and not self.mount:
			raise ValueError('direction commanded to fixed sensor')
		else:
			self.mount.move(x=angle)

		measurements = []
		for i in range(3):
			measurements.append(self.driver.us_dist(self.pin))

		print 'Sensed {0} cm at angle {1}'.format(median(measurements), angle)

		return int(self.error_fnc(median(measurements)))

	def sense_swath(self, center=0, width=0, num_measurements=1,
					return_all_measurements=False):
		"""Sense the distance at a given general direction.

		Args:
		center - the center of the swath to measure, in degrees, where 0 is
			straight ahead.
		width - the width of the swath, in degrees.
		num_measurements - the number of measurements to take, evenly spread
			across width, centered on center.
		return_all_measurements - if True, returns a list of all measurements
			taken.

		Returns distance in cm.  Measurements are taken at the given angle, and
			at +/- <interval> degrees from that angle.  The smallest distance
			is returned, unless return_all_measurements is True, in which case
			a list of all measurements is returned.
		"""

		measurements = []
		left_limit = int(center) - int(width / 2)
		right_limit = int(center) + int(width / 2)
		interval = int(width / ((num_measurements - 1) or 1))
		
		for a in range(left_limit, right_limit + 1, interval):
			try:
				measurements.append(self.sense_distance(a % 360))
			except ValueError:
				pass  # silently accept out-of-arc angles

		if not measurements:
			raise ValueError('unable to sense at angle {0}'.format(angle))
		
		if return_all_measurements:
			return measurements
		else:
			return min(measurements)
