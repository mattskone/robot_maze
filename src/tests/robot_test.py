"""Unit tests for the robot module."""

import unittest

from mock import MagicMock

import robot


class RobotTests(unittest.TestCase):
	"""Unit tests for the Robot class."""

	def setUp(self):
		self.mock_sensor = MagicMock()
		self.r = robot.Robot(driver_module='tests.gopigo_stub')
		self.r.sensor = self.mock_sensor

	def test_init(self):
		"""Verify robot's attributes."""

		self.assertEqual(self.r.state, None)
		self.assertEqual(self.r.sensor, self.mock_sensor)

	def test_run(self):
		"""Verify run() is delegated to the robot's state."""

		mock_state = MagicMock()
		mock_state.run.return_value = True

		with self.assertRaises(AttributeError):
			self.r.run()

		self.r.state = mock_state
		self.assertTrue(self.r.run())
		mock_state.run.assert_called_once_with()

	def test_sense(self):
		"""Verify sense() is delegated to the sensor."""

		self.mock_sensor.sense.return_value = 50
		self.assertEqual(self.r.sense(foo='bar'), 50)
		self.mock_sensor.sense.assert_called_once_with(foo='bar')

	def test_stop(self):
		"""Verify stop() is delegated to the driver."""

		self.r.stop()
		self.assertEqual(self.r.driver.calls[-1], 'stop()')
