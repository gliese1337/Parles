from ParlesStructs import *

def call(state, a, b):
	quot, penv = a
	frame = ARecord(quot,penv,state.frame,state.ip)
	state.frame = frame
	state.ip = -1
	return state, None
	
def pop(state, a, b):
	v, state.stack = state.stack
	return state, v

optable = {
	'add': lambda s, a, b: (s, a + b),
	'get': lambda s, a, b: (s, a),
	'call': call,
	'pop': pop
}