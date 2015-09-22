"""Implementation for a movable mount."""

import time


class SwivelMount(object):
	"""A mount that can swivel through a horizontal arc."""

	def _is_valid_angle(self, angle):
		"""Return True if angle between 0 and 359."""

		return 0 <= angle < 360

	def _is_allowable_angle(self, angle):
		"""Return True if angle is within left/right limits."""

		if self.max_left < self.max_right:
			return self.max_left <= angle <= self.max_right
		else:
			return (angle >= self.max_left) or (angle <= self.max_right)

	def __init__(self, driver=None, center=0, servo_center=90,
				 clockwise_servo=False, arc=180):
		"""Create an instance of a SwivelMount.

		Args:
		driver - a Driver instance, for commanding the controller
		center - the directional center of the mount's alignment, relative
			to the centerline of the robot, in degrees
		servo_center - the servo angle necessary to center the mount on the
			'center' direction, in degrees
		clockwise_servo - if True, increasing the servo angle causes the mount
			to swivel clockwise when viewed from above.
		arc - the allowable travel of the mount, in degrees
		swivel_plane - the plane through which the mount can swivel.  'x' is
			horizontal, 'y' is vertical.
		"""

		if (not self._is_valid_angle(center) or
			not self._is_valid_angle(arc) or
			not self._is_valid_angle(servo_center)):
				raise ValueError('all angle values must be in range 0-359.')

		self.driver = driver
		self.mount_center = center
		self.servo_center = servo_center
		self.clockwise_servo = clockwise_servo
		self.max_right = center + (arc / 2) % 360
		self.max_left = 360 - abs(center - (arc / 2))

		self.current_angle = center
		self.center()

	def _mount_angle_to_servo_angle(self, angle):
		"""Return correct servo angle for desired mount angle."""

		if self.clockwise_servo:
			return (self.servo_center + angle) % 360
		else:
			return (self.servo_center - angle) % 360

	def move(self, x=0, y=0):
		"""Swivel the mount to the specified direction.

		Args:
		x - the desired horizontal direction
		y - not supported for SwivelMount
		"""

		if not all([self._is_valid_angle(x), self._is_allowable_angle(x)]):
			raise ValueError('angle must be in range {0}-{1}'.format(
					self.max_left, self.max_right
				)
			)
		if y:
			raise ValueError('vertical angle not supported on SwivelMount')

		x = self._mount_angle_to_servo_angle(x)
		self.driver.servo(x)

		# Allow sufficient time to complete the movement before returning:
		delay_times = [0.2, 0.4, 0.6, 0.8]  # 0.2 secs per 90 degrees of travel
		time.sleep(delay_times[abs(self.current_angle - x) / 90])

	def center(self):
		"""Center the mount."""

		self.move(x=self.mount_center)
