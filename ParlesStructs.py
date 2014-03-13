from collections import namedtuple

#register file size, environment size, instruction list
class Quotation(namedtuple('Quotation', ['id', 'rsize', 'vsize', 'instrs', 'dskip'])):
	def __repr__(self):
		id, rsize, vsize, instrs, dskip = self
		return id+'(%d, %d, %d):\n'%(rsize,vsize,dskip)+'\n'.join(map(lambda i: str(i), instrs))

def argstr(arg):
	spec, index = arg
	if spec == -3:
		return ""
	if spec == -2:
		return '#'+str(index)
	if spec == -1:
		return 'r'+str(index)
	return "["+str(spec)+"]"+str(index)
	
class Instr(namedtuple('Instr', ['dest', 'op', 'arg1', 'arg2'])):
	def __repr__(self):
		dest, op, arg1, arg2 = self
		#get destination
		spec, index = dest
		if spec == 's':
			rstr = 's'
		elif spec == 'r' or spec == 'v':
			rstr = spec+str(index)
		else:
			rstr = 'n'
		rstr += '\t= '+op
		astr = argstr(arg1)
		if astr: rstr += ' '+astr
		astr = argstr(arg2)
		if astr: rstr += ' '+astr
		return rstr

#associated quotation ID, access link (parent environment), list of variables
class Env():
	def __init__(self,quot,parent):
		self.qid = quot.id
		self.parent = parent
		self.vars = [None]*quot.vsize
	
	def __repr__(self):
		return 'id: %s\t%d\n'%(self.qid,len(self.vars))+(str(self.parent) if self.parent else '')

#quotation & access link (parent environment)
Closure = namedtuple('Closure', ['quot', 'penv'])

#environment, register file, quotation, return record, return IP
class ARecord():
	def __init__(self,quot,penv,prec,pip):
		env = penv if quot.vsize == 0 else Env(quot,penv)
		self.env = env
		self.rfile = [None]*quot.rsize
		self.quot = quot
		self.r_rec = prec
		self.r_ip = pip

#activation record (stack frame), instruction pointer, stack
class MState():
	def __init__(self,frame,ip,stack):
		self.frame = frame
		self.ip = ip
		self.stack = stack
	
	@property
	def instr(self):
		return self.frame.quot.instrs[self.ip]
	
	@property
	def ended(self):
		return self.ip >= len(self.frame.quot.instrs)