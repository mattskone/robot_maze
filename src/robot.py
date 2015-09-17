"""An implementation of a state-driven robot."""

class Robot(object):
	"""The Robot class.

	Set the robot in motion by initializing a Robot object and calling run().
	The robot will run autonomously until a goal state is reached or some
	unrecoverable exception occurs.
	"""

	def __init__(self):
		"""Initialize the robot attributes."""
		self.state = None

	def run(self):
		"""Set the robot in motion.

		Execution is delegated to the current state.

		Returns whatever value is returned from the underlying state.
		"""

		if not self.state:
			# TODO: make the robot determine it's state before proceding
			raise AttributeError('State attribute not set on Robot.')
		return self.state.run()
