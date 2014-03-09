from collections import namedtuple

#register file size, environment size, instruction list
Quotation = namedtuple('Quotation', ['id', 'rsize', 'vsize', 'instrs'])
Instr = namedtuple('Instr', ['dest', 'op', 'arg1', 'arg2'])

#associated quotation ID, access link (parent environment), list of variables
class Env():
	def __init__(self,quot,parent):
		self.qid = quot.id
		self.parent = parent
		self.vars = [None]*quot.vsize

#quotation & access link (parent environment)
Closure = namedtuple('Closure', ['quot', 'penv'])

#environment, register file, quotation, return record, return IP
class ARecord():
	def __init__(self,quot,penv,prec,pip):
		self.env = Env(quot,penv)
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