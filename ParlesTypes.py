from collections import namedtuple

class TypeVar(str):
	pass

class AtomType():
	def __init__(self, val):
		self.val = val

	def __repr__(self):
		return self.val
	
	def __eq__(self,other):
		return isinstance(other, AtomType) and self.val == other.val

class StackType(namedtuple('StackType', ['row', 'top'])):
	def __repr__(self):
		return str(self.row) + ' '+' '.join(map(str,self.top))
		
class FuncType(namedtuple('FuncType', ['input', 'output'])):
	def __repr__(self):
		return '('+str(self.input)+' -> '+str(self.output)+')'

vcount = 0
def genvar():
	global vcount
	vcount += 1
	return TypeVar("#%d"%(vcount,))

def reset():
	global vcount
	vcount = 0

def TypeName(val):
	if val == "any":
		return genvar()
	return AtomType(val)
