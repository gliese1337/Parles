from ParlesStructs import *

def call(state, a, b):
	quot, penv = a
	frame = state.frame
	if state.ended:
		#tail call- don't save the current frame
		state.frame = ARecord(quot, penv, frame.r_rec, frame.r_ip)
	else:
		state.frame = ARecord(quot, penv, frame, state.ip)
	state.ip = 0
	return state, None

def clos(state, quot, b):
	#compute the access link
	env = state.frame.env
	for _ in xrange(quot.dskip,0,-1):
		env = env.parent
	return state, Closure(quot,env)

def pop(state, a, b):
	v, state.stack = state.stack
	return state, v

def _print(state, a, b):
	print a
	return state, None

def jz(state, a, b):
	if a == 0:
		state.ip += b
	return state, None

def jmp(state, a, b):
	state.ip += a
	return state, None

def dmod(state, a, b):
	c, d = divmod(a, b)
	state.stack = (c, (d, state.stack))
	return state, None

optable = {
	'mov': lambda s, a, b: (s, a),
	'add': lambda s, a, b: (s, a + b),
	'sub': lambda s, a, b: (s, a - b),
	'mul': lambda s, a, b: (s, a * b),
	'div': lambda s, a, b: (s, a / b),
	'mod': lambda s, a, b: (s, a % b),
	'lt': lambda s, a, b: (s, 1 if a < b else 0),
	'gt': lambda s, a, b: (s, 1 if a > b else 0),
	'eq': lambda s, a, b: (s, 1 if a == b else 0),
	'not': lambda s, a, b: (s, 1 if not a else 0),
	'dmod': dmod,
	'jz': jz,
	'jmp': jmp,
	'clos': clos,
	'print': _print,
	'call': call,
	'pop': pop
}