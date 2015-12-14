"""Top-level script for letting the robot run."""

import sys
import time

import mount
import robot
import sensor
import state


def sensor_error(raw_sensor_value):
	"""Actual sensor error derived from field tests."""
	return (raw_sensor_value + 2.5) / 1.32


def go():
	r = robot.Robot()
	m = mount.SwivelMount(driver=r.driver, servo_center=93)
	s = sensor.UltrasonicSensor(driver=r.driver,
								mount=m,
								error_fnc=sensor_error)
	cs = state.CorridorState(robot=r)

	r.distance_sensor = s
	r.state = cs

	print 'Voltage: {0}'.format(r.volt)
	print 'Starting in 3 seconds...'
	time.sleep(3)
	try:
		r.run()
	except KeyboardInterrupt:
		r.stop()
		sys.exit()


if __name__ == '__main__':
	go()
