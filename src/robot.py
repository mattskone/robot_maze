"""An implementation of a state-driven autonomous robot."""


MOTOR_LEFT = 0			# Index of the left motor
MOTOR_RIGHT = 1			# Index of the right motor
SERVO_CENTER = 93		# Servo angle for centerline
TRIM_STRAIGHT = 90		# Trim setting for straight movement
DEFAULT_SPEED = 60		# Slowest speed without stalling
SENSOR_PIN = 15			# Pin number on which the US sensor is connected


class Robot(object):
	"""The Robot class.

	Set the robot in motion by initializing a Robot object and calling run().
	The robot will run autonomously until a goal state is reached or some
	unrecoverable exception occurs.
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

		global driver
		driver = __import__(driver_module)
		driver.stop()
		driver.set_speed(DEFAULT_SPEED)
		driver.servo(SERVO_CENTER)
		driver.trim_write(TRIM_STRAIGHT)

		self.state = None

	def run(self):
		"""Set the robot in motion.

		Execution is delegated to the current state.

		Returns whatever value is returned from the underlying state.
		"""

		if not self.state:
			# TODO: make the robot determine its state before proceding
			raise AttributeError('State attribute not set on Robot.')
		return self.state.run()
