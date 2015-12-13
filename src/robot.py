"""An implementation of a state-driven autonomous robot."""

from importlib import import_module
import time

import mount
import sensor


MOTOR_LEFT = 0			# Index of the left motor
MOTOR_RIGHT = 1			# Index of the right motor
TRIM_STRAIGHT = -10		# Trim setting for straight movement
DEFAULT_SPEED = 60  	# Slowest speed without stall (60/120 for batt/cable)
TURN_SPEED = 10			# Added speed for the outside wheel when turning
MAX_TURN_RATIO = 1.2	# Max ratio of outside wheel to inside wheel speeds
ROTATING_DEGREES_PER_TICK = 10	# Degrees of robot rotation in one encoder tick
TURNING_DEGREES_PER_TICK = 5	# Degrees of robot turn in one encoder tick


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
		self.distance_sensor = None
		self.state = None

		# Initialize motor components
		self.driver.stop()
		self.speed = [0, 0]  # [left, right motor]
		self.driver.set_speed(DEFAULT_SPEED)
		self.driver.trim_write(TRIM_STRAIGHT)
		self.left_encoder = 0
		self.right_encoder = 0

	def run(self):
		"""Set the robot in motion.

		Execution is delegated to the current state.

		Returns whatever value is returned from the underlying state.
		"""

		if not self.state:
			# TODO: make the robot determine its state before proceding
			raise AttributeError('State attribute not set on Robot.')
		return self.state.run()

	@property
	def degrees_turned(self):
		"""Return the net degrees of turn since last accessed.

		Positive values indicate a net right turn, and negative values
		indicate a net left turn.
		"""

		left_encoder = self.driver.enc_read(MOTOR_LEFT)
		right_encoder = self.driver.enc_read(MOTOR_RIGHT)
		diff_left = left_encoder - self.left_encoder
		diff_right = right_encoder - self.right_encoder
		degrees = (diff_left - diff_right) * TURNING_DEGREES_PER_TICK

		self.left_encoder = left_encoder
		self.right_encoder = right_encoder

		return degrees

	def dist(self, angle=0):
		"""Take an return a distance sensor reading in the direction given."""

		if not self.distance_sensor:
			raise ValueError('no sensor configured')
		
		return self.distance_sensor.sense(angle)

	def stop(self):
		self.distance_sensor.center()  # Because OCD is a thing
		self.driver.stop()

	def fwd(self):
		self.driver.set_speed(DEFAULT_SPEED)
		self.driver.fwd()
		self.speed = [DEFAULT_SPEED, DEFAULT_SPEED]

	def rotate(self, degrees=0):
		"""Rotate the robot in place the given number of degrees.

		Args:
		degrees - the number of degrees to rotate (-360 to 360).  Positive
			degrees command a right-hand rotation, and negative degrees command
			a left-hand rotation.
		"""

		self.driver.stop()
		if degrees > 0:
			self.driver.enc_tgt(1, 0, int(degrees / ROTATING_DEGREES_PER_TICK))
			self.driver.right_rot()
		else:
			self.driver.enc_tgt(0, 1, abs(int(degrees / ROTATING_DEGREES_PER_TICK)))
			self.driver.left_rot()

	def steer(self, steering_factor):
		"""Adjust wheel speeds to adjust turning rate.

		Args:
		steering_factor - a multiple to scale TURN_SPEED, which computes the
			new speed of the outside wheel of the turn.  Postive values result
			in a left turn, and negative values in a right turn.
		"""

		turn_wheel_speed = min([
			int(DEFAULT_SPEED + abs(steering_factor) * TURN_SPEED),
			int(DEFAULT_SPEED * MAX_TURN_RATIO)
		])

		if steering_factor > 0:
			self.speed = [DEFAULT_SPEED, turn_wheel_speed]
		elif steering_factor < 0:
			self.speed = [turn_wheel_speed, DEFAULT_SPEED]
		else:
			self.speed = [DEFAULT_SPEED, DEFAULT_SPEED]
		self.driver.set_left_speed(self.speed[0])
		self.driver.set_right_speed(self.speed[1])
