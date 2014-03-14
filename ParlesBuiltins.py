from ParlesStructs import *

def call(state, a, b):
	quot, penv = a
	frame = ARecord(quot,penv,state.frame,state.ip)
	state.frame = frame
	state.ip = -1
	return state, None

def clos(state, quot, b):
	#compute the access link
	skip = quot.dskip
	env = state.frame.env
	while skip > 0:
		env = env.parent
		skip -= 1
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