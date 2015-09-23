"""An implementation of a state-driven autonomous robot."""

from importlib import import_module
import time

import mount
import sensor


MOTOR_LEFT = 0			# Index of the left motor
MOTOR_RIGHT = 1			# Index of the right motor
TRIM_STRAIGHT = 90		# Trim setting for straight movement
DEFAULT_SPEED = 60		# Slowest speed without stalling
TURN_SPEED = 10			# Added speed for the outside wheel when turning


class Robot(object):
	"""The Robot class.

	Set the robot in motion by initializing a Robot object and calling run().
	The robot will run autonomously until a goal state is reached or some
	unrecoverable exception occurs.  Or until you step on it.
	"""

	def __init__(self, driver_module='gopigo'):
		"""Initialize the robot attributes.

		Args:
		driver - the name of the module containing all of the robot control
			commands.  Default is the 'gopigo' module, which will normally be
			used for robot operation.  However, a stub module can be
			substituted for testing purposes.  This delayed import allows for
			development and testing without having to install all of the gopigo
			dependencies.

		"""

		self.driver = import_module(driver_module)
		self.sensor = None
		self.state = None

		# Initialize motor components
		self.driver.stop()
		self.speed = [0, 0]  # [left, right motor]
		self.driver.set_speed(DEFAULT_SPEED)
		self.driver.trim_write(TRIM_STRAIGHT)

	def run(self):
		"""Set the robot in motion.

		Execution is delegated to the current state.

		Returns whatever value is returned from the underlying state.
		"""

		if not self.state:
			# TODO: make the robot determine its state before proceding
			raise AttributeError('State attribute not set on Robot.')
		return self.state.run()

	def sense(self, *args, **kwargs):
		"""Take an return a sensor reading."""

		if not self.sensor:
			raise ValueError('no sensor configured')
		
		return self.sensor.sense(*args, **kwargs)

	def stop(self):
		self.driver.stop()

	def fwd(self):
		self.driver.set_speed(DEFAULT_SPEED)
		self.driver.fwd()
		self.speed = [DEFAULT_SPEED, DEFAULT_SPEED]

	def steer(self, steering_factor):
		"""Adjust wheel speeds to adjust turning rate.

		Args:
		steering_factor - a multiple to scale TURN_SPEED, which computes the
			new speed of the outside wheel of the turn.  Postive values result
			in a left turn, and negative values in a right turn.
		"""

		turn_wheel_speed = DEFAULT_SPEED + abs(steering_factor) * TURN_SPEED

		if steering_factor > 0:
			self.speed = [DEFAULT_SPEED, turn_wheel_speed]
		elif steering_factor < 0:
			self.speed = [turn_wheel_speed, DEFAULT_SPEED]
		else:
			self.speed = [DEFAULT_SPEED, DEFAULT_SPEED]

		self.driver.set_left_speed(self.speed[0])
		self.driver.set_right_speed(self.speed[1])
