"""Unit tests for the robot module."""

import unittest

from mock import MagicMock

import robot


class RobotTests(unittest.TestCase):
	"""Unit tests for the Robot class."""

	def setUp(self):
		self.mock_sensor = MagicMock()
		self.r = robot.Robot(driver_module='tests.gopigo_stub')
		self.r.distance_sensor = self.mock_sensor

	def test_init(self):
		"""Verify robot's attributes."""

		self.assertEqual(self.r.state, None)
		self.assertEqual(self.r.distance_sensor, self.mock_sensor)
		self.assertEqual(self.r.speed, [0, 0])

	def test_volt(self):
		"""Verify volt() returns current battery voltage."""

		TEST_VOLTAGE = 9.5
		self.r.driver.volt = MagicMock()
		self.r.driver.volt.return_value = TEST_VOLTAGE

		self.assertEqual(self.r.volt, TEST_VOLTAGE)

	def test_degrees_turned(self):
		"""Verify degrees turned is calculated correctly."""

		def enc_read(motor):
			if motor == 0:
				return 150
			else:
				return 140

		self.r.driver.enc_read = enc_read
		self.r.left_encoder = 100
		self.r.right_encoder = 95

		expected_degrees = 25  # Net encoder ticks * 5 degrees per tick
		self.assertEqual(self.r.degrees_turned, expected_degrees)
		self.assertEqual(self.r.left_encoder, 150)
		self.assertEqual(self.r.right_encoder, 140)

	def test_run(self):
		"""Verify run() is delegated to the robot's state."""

		mock_state = MagicMock()
		mock_state.run.return_value = True

		with self.assertRaises(AttributeError):
			self.r.run()

		self.r.state = mock_state
		self.assertTrue(self.r.run())
		mock_state.run.assert_called_once_with()

	def test_dist(self):
		"""Verify dist() is delegated to the distance sensor."""

		self.mock_sensor.sense.return_value = 50
		self.assertEqual(self.r.dist(45), 50)
		self.mock_sensor.sense.assert_called_once_with(45)

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

	def test_rotate(self):
		"""Verify rotate() is executed correctly."""

		expected_calls = ['stop()',
						  'enc_tgt(1, 0, 18)',
						  'right_rot()']
		self.r.rotate(degrees=180)
		self.assertEqual(self.r.driver.calls[-3:], expected_calls)

		expected_calls = ['stop()',
						  'enc_tgt(0, 1, 9)',
						  'left_rot()']
		self.r.rotate(degrees=-90)
		self.assertEqual(self.r.driver.calls[-3:], expected_calls)

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
