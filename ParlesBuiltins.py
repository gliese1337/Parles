from ParlesStructs import *

def call(state, a, b):
	quot, penv = a
	frame = ARecord(quot,penv,state.frame,state.ip)
	state.frame = frame
	state.ip = -1
	return state, None

def clos(state, a, b):
	return state, Closure(a,state.frame.env)
	
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
	'add': lambda s, a, b: (s, a + b),
	'mov': lambda s, a, b: (s, a),
	'lt': lambda s, a, b: (s, 1 if a < b else 0),
	'dmod': dmod,
	'jz': jz,
	'jmp': jmp,
	'clos': clos,
	'print': _print,
	'call': call,
	'pop': pop
}