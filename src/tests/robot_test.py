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
		self.assertEqual(self.r.speed, [0, 0])

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
		self.mock_sensor.center.assert_called_once_with()
		self.assertEqual(self.r.driver.calls[-1], 'stop()')

	def test_fwd(self):
		"""Verify fwd() is delegated to the driver."""

		self.r.fwd()
		self.assertEqual(self.r.speed,
						 [robot.DEFAULT_SPEED, robot.DEFAULT_SPEED])
		self.assertEqual(self.r.driver.calls[-1], 'fwd()')
		self.assertEqual(self.r.driver.calls[-2],
						 'set_speed({0})'.format(robot.DEFAULT_SPEED))

	def test_steer(self):
		"""Verify steer() is translated correctly to driver."""

		self.r.speed = [robot.DEFAULT_SPEED, robot.DEFAULT_SPEED]

		# Steer to the left
		self.r.steer(1.2)
		expected_speed = int(robot.DEFAULT_SPEED + 1.2 * robot.TURN_SPEED)
		self.assertEqual(
			self.r.speed,
			[robot.DEFAULT_SPEED, expected_speed]
		)
		self.assertEqual(self.r.driver.calls[-1],
						 'set_right_speed({0})'.format(expected_speed))
		self.assertEqual(self.r.driver.calls[-2],
						 'set_left_speed({0})'.format(robot.DEFAULT_SPEED))

		# Steer to the right
		self.r.steer(-1)
		expected_speed = robot.DEFAULT_SPEED + robot.TURN_SPEED
		self.assertEqual(
			self.r.speed,
			[expected_speed, robot.DEFAULT_SPEED]
		)
		self.assertEqual(self.r.driver.calls[-1],
						 'set_right_speed({0})'.format(robot.DEFAULT_SPEED))
		self.assertEqual(self.r.driver.calls[-2],
						 'set_left_speed({0})'.format(expected_speed))

		# Steer too much to the right
		self.r.steer(-5)
		expected_speed = int(robot.DEFAULT_SPEED * robot.MAX_TURN_RATIO)
		self.assertEqual(
			self.r.speed,
			[expected_speed, robot.DEFAULT_SPEED]
		)
		self.assertEqual(self.r.driver.calls[-1],
						 'set_right_speed({0})'.format(robot.DEFAULT_SPEED))
		self.assertEqual(self.r.driver.calls[-2],
						 'set_left_speed({0})'.format(expected_speed))

		# Steer straight ahead
		self.r.steer(0)
		self.assertEqual(
			self.r.speed,
			[robot.DEFAULT_SPEED, robot.DEFAULT_SPEED]
		)
		self.assertEqual(self.r.driver.calls[-1],
						 'set_right_speed({0})'.format(robot.DEFAULT_SPEED))
		self.assertEqual(self.r.driver.calls[-2],
						 'set_left_speed({0})'.format(robot.DEFAULT_SPEED))
