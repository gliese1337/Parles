from ParlesStructs import *

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

def run(qlist, entry):
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

def parse_arg(arg):
	if arg[0] == '#':
		return (-2, int(arg[1:]))
	if arg[0] == '"':
		from base64 import b64decode
		return (-2, b64decode(arg[1:]))
	if arg[0] == 'r':
		return (-1, int(arg[1:]))
	return tuple(map(int, arg[1:].split(']')))

def parse_instr(line):
	fields = line.split(' ')
	flen = len(fields)
	sdest, _, op = fields[:3]
	arg1, arg2 = (-3, 0), (-3, 0)

	if sdest in ['s', 'n']:
		dest = (sdest, 0)
	else:
		dest = (sdest[0], int(sdest[1:]))

	if flen > 3:
		arg1 = parse_arg(fields[3])
		if flen > 4:
			arg2 = parse_arg(fields[4])

	return Instr(dest, op, arg1, arg2)

def load(lines):
	entry = int(lines.next())
	quots, instrs = [], None
	for line in map(lambda l: l.strip(), lines):
		if line[0] == 'q':
			if instrs is not None:
				quots.append(Quotation("", rsize, vsize, instrs, dskip))
			rsize, vsize, dskip = map(int, line.split(' ')[1:])
			instrs = []
		else:
			instrs.append(parse_instr(line))
	if instrs is not None:
		quots.append(Quotation("", rsize, vsize, instrs, dskip))
	return quots, entry


if __name__ == "__main__":
	import sys
	try:
		final = run(*load(sys.stdin))
		print "Final Stack:", final
	except StopIteration:
		print "VM: No Program"