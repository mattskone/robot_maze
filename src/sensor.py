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

		# print 'Sensed {0} cm at angle {1}'.format(median(measurements), angle)

		return int(self.error_fnc(median(measurements)))

	def sense_swath(self, angle):
		"""Sense the distance at a given general direction.

		Args:
		angle - the center of the swath to measure, where 0 is straight ahead.

		Returns distance in cm.  Measurements are taken at the given angle, and
			at +/- 15 degrees from that angle, for a 30-degree swath. The
			smallest distance is returned.
		"""

		measurements = []
		for a in range(angle - 20, angle + 40, 20):
			try:
				measurements.append(self.sense_distance(a % 360))
			except ValueError:
				pass  # silently accept out-of-arc angles

		if not measurements:
			raise ValueError('unable to sense at angle {0}'.format(angle))
		else:
			return min(measurements)
