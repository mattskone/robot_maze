"""Implementation for a movable mount."""

import time

SERVO_SHORT_MOVE_TIME = 0.2
SERVO_LONG_MOVE_TIME = 0.4


class SwivelMount(object):
	"""A mount that can swivel through an arc in 2 dimensions."""

	def _is_valid_angle(self, angle):
		"""Return True if angle between 0 and 359."""

		return 0 <= angle < 360

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
		"""

		if (not self._is_valid_angle(center) or
			not self._is_valid_angle(arc) or
			not self._is_valid_angle(servo_center)):
				raise ValueError('All angle values must be in range 0-359.')

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

	def swivel(self, angle):
		"""Swivel the mount to the specified angle."""

		if not 0 <= angle < 360:
			raise ValueError('Angle must be in range 0-359.')

		angle = self._mount_angle_to_servo_angle(angle)
		self.driver.servo(angle)

		# Allow sufficient time to complete the movement before returning:
		delay_times = [0.2, 0.4, 0.6, 0.8]  # 0.2 secs per 90 degrees of travel
		time.sleep(delay_times[abs(self.current_angle - angle) / 90])

	def center(self):
		"""Center the mount."""

		self.swivel(self.mount_center)
