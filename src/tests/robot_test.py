"""Unit tests for the robot module."""

import unittest

from mock import MagicMock

from robot import Robot


class RobotTests(unittest.TestCase):
	"""Unit tests for the Robot class."""

	def test_init(self):
		"""Verify robot's attributes."""

		r = Robot()
		self.assertEqual(r.state, None)

	def test_run(self):
		"""Verify run() is delegated to the robot's state."""

		mock_state = MagicMock()
		mock_state.run.return_value = True

		r = Robot()

		with self.assertRaises(AttributeError):
			r.run()

		r.state = mock_state
		self.assertTrue(r.run())
		mock_state.run.assert_called_once_with()
