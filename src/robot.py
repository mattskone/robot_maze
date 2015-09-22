"""An implementation of a state-driven autonomous robot."""

from importlib import import_module
import time

import mount
import sensor


MOTOR_LEFT = 0			# Index of the left motor
MOTOR_RIGHT = 1			# Index of the right motor
TRIM_STRAIGHT = 90		# Trim setting for straight movement
DEFAULT_SPEED = 60		# Slowest speed without stalling
TURN_SPEED_OFFSET = 10	# Added speed for the outside wheel when turning


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
