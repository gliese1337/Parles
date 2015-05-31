#Compiled program:
#	list of quotation objects and entry point

U, C, R = -3, -2, -1
def getv(var, rec):
	t, n = var
	if t == U: return None         #unused argument
	if t == C: return n            #constant
	if t == R: return rec.rfile[n] #register variable

	#display variable
	env = rec.env
	for _ in xrange(t,0,-1):
		env = env.parent
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
		#implicit return
		if state.ended:
			state.ip = state.frame.r_ip + 1
			state.frame = state.frame.r_rec
			continue

		#decode
		((dtype, n), op, a1, a2) = state.instr
		v1 = getv(a1, state.frame)
		v2 = getv(a2, state.frame)

		#print '\t', state.instr, '\n\t\t\t', (v1, v2)

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

	return list(iter_stack(state.stack))