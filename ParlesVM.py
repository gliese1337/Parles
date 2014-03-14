#Compiled program:
#	list of quotation objects and entry point

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
		#print env
		env = env.parent
		t = t - 1
	#print env
	return env.vars[n]

def iter_stack(stack):
	while stack is not None:
		a, stack = stack
		yield a

def run(entry, qlist):
	from ParlesStructs import *
	from ParlesVMInstructions import optable
	#set up the global environment
	genv = Env(Quotation('global',0,0,[],0),None)
	genv.vars = qlist
	#start up the main function
	main = qlist[entry]
	state = MState(ARecord(main,genv,None,0),0,None)
	while state.frame is not None:
		
		#decode
		((dtype, n), op, a1, a2) = state.instr
		#print dtype, n, op, a1, a2
		v1 = getv(a1, state.frame)
		v2 = getv(a2, state.frame)
		#print '\t', dtype, n, op, v1 if v1 else '', v2 if v2 else ''
		
		#execute
		state, output = optable[op](state, v1, v2)
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