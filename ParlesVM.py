from ParlesStructs import *

#Compiled program:
#	list of quotation objects

U, C, R = -3, -2, -1	
def getv(var, rec):
	t, n = var
	if t == U: #unused argument
		return None
	if t == C: #constant
		return n
	if t == R: #register
		return rec.rfile[n]
	#variable
	env = rec.env
	while t > 0:
		env = env.parent
		t = t - 1
	return env.vars[n]

def iter_stack(stack):
	while stack is not None:
		a, stack = stack
		yield a

def run(prog):
	from ParlesBuiltins import optable
	quot = prog[0]
	#this is a bad hack that turns *everything* into a globally-scoped closure
	genv = Env(Quotation('global',0,0,[]),None)
	genv.vars = map(lambda q: Closure(q,genv), prog)
	state = MState(ARecord(quot,genv,None,0),0,None)
	while state.frame is not None:
		
		#decode
		((dtype, n), op, a1, a2) = state.instr
		
		#execute
		state, output = optable[op](state, getv(a1, state.frame), getv(a2, state.frame))
		state.ip += 1
		
		#store
		if dtype == 's':
			state.stack = (output, state.stack)
		elif dtype == 'r':
			state.frame.rfile[n] = output
		elif dtype == 'v':
			state.frame.env.vars[n] = output
		elif dtype == 'n':
			pass
		
		#implicit return
		if state.ended:
			state.ip = state.frame.r_ip + 1
			state.frame = state.frame.r_rec
	
	return list(iter_stack(state.stack))