"""Unit tests for the robot module."""

import unittest

from mock import MagicMock

import robot
from robot import Robot


class RobotTests(unittest.TestCase):
	"""Unit tests for the Robot class."""

	def setUp(self):
		self.r = Robot(driver_module='gopigo_stub')

	def test_init(self):
		"""Verify robot's attributes."""

		self.assertEqual(self.r.state, None)

	def test_run(self):
		"""Verify run() is delegated to the robot's state."""

		mock_state = MagicMock()
		mock_state.run.return_value = True

		with self.assertRaises(AttributeError):
			self.r.run()

		self.r.state = mock_state
		self.assertTrue(self.r.run())
		mock_state.run.assert_called_once_with()
