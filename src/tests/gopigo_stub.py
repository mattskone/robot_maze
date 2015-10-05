"""A stub for the gopigo module."""

calls = []

def servo(angle):
	calls.append('servo({0})'.format(angle))

def set_speed(speed):
	calls.append('set_speed({0})'.format(speed))

def set_left_speed(speed):
	calls.append('set_left_speed({0})'.format(speed))

def set_right_speed(speed):
	calls.append('set_right_speed({0})'.format(speed))

def stop():
	calls.append('stop()')

def fwd():
	calls.append('fwd()')

def enc_tgt(*args):
	calls.append('enc_tgt{0}'.format(args))

def right_rot():
	calls.append('right_rot()')

def trim_write(trim):
	calls.append('trim_write({0})'.format(trim))

def us_dist(pin):
	calls.append('us_dist({0})'.format(pin))
	return 600  # approximate max range
