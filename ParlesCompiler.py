from collections import defaultdict, namedtuple
from ParlesAST import *
from ParlesTypes import *
from ParlesParser import parse
from ParlesStructs import Quotation, Instr
from ParlesCompose import compose

class VarTable():
	counts = defaultdict(int)
	@staticmethod
	def reset():
		VarTable.counts = defaultdict(int)
	
	def __init__(self,parent):
		self.parent = parent
		self.table = {}
	
	def __contains__(self,item):
		return (item in self.table) or (item in self.parent if self.parent else False)
	
	def __getitem__(self,index):
		if index in self.table:
			return self.table[index]
		if self.parent and (index in self.parent):
			return self.parent[index]
		return None
		
	def addId(self,index):
		count = VarTable.counts[index] + 1
		VarTable.counts[index] = count
		value = index + str(count)
		self.table[index] = value
		return value

	def addVar(self,index):
		if index in self.table:
			raise Exception("Symbol Table Error")
		return self.addId(index)

def lift_block(block):
	node = block.body
	while isinstance(node, Seq) or isinstance(node, Pipe):
		left = node.left
		while isinstance(left, Block):
			nblock = left
			node.left = nblock.body
			block.args.extend(nblock.args)
			left = node.left
		node = node.left
	
def _alphavary(node, vtable):
	if isinstance(node, Literal):
		return node
	if isinstance(node, Word):
		val = node.val
		if val in vtable:
			node.val = vtable[val]
		return node
	if isinstance(node, Seq):
		left = _alphavary(node.left, vtable)
		right = _alphavary(node.right, vtable)
		return Seq(left, right)#, vtable.addId('seq'))
	if isinstance(node, Pipe):
		left = _alphavary(node.left, vtable)
		right = _alphavary(node.right, vtable)
		return Pipe(left, right)#, vtable.addId('pipe'))
	if isinstance(node, Block) or isinstance(node, Quote):
		if node.args:
			vtable = VarTable(vtable)
			for a in node.args:
				a.val = vtable.addVar(a.val)
		#node.id = vtable.addId('quote')
		node.body = _alphavary(node.body, vtable)
		#lift_block(node)
		return node

def alphavary(node):
	VarTable.reset()
	return _alphavary(node, VarTable(None))

class TypeEnv():
	def __init__(self, parent=None):
		self.parent = parent
		self.table = {}
	
	def __contains__(self, item):
		return (item in self.table) or (item in self.parent if self.parent else False)
	
	def __getitem__(self, index):
		if index in self.table:
			return self.table[index]
		if self.parent and (index in self.parent):
			return self.parent[index]
		return None
		
	def extend(self, vardict):
		nenv = TypeEnv(self)
		nenv.table.update(vardict)
		return nenv

def produce(t):
	row = genvar()
	return FuncType(StackType(row,[]),StackType(row, [t]))
	
def promote(t):
	if isinstance(t, FuncType): return t
	return produce(t)

def seqtype(node, tenv):
	ltype = promote(typecheck(node.left, tenv))
	rtype = promote(typecheck(node.right, tenv))
	return compose(ltype, rtype)

def pipetype(node, tenv):
	ltype = promote(typecheck(node.left, tenv))
	rtype = promote(typecheck(node.right, tenv))
	if len(ltype.output.top) != len(rtype.input.top):
		raise Exception("Pipe mismatch")
	return compose(ltype, rtype)

def blocktype(node, tenv):
	nenv = tenv.extend({a.val: a.type for a in node.args})
	bodytype = typecheck(node.body, nenv)
	bodytype.input.top.extend(reversed(map(lambda a: a.type, node.args)))
	return bodytype

def _typecheck(node, tenv):
	if isinstance(node, Literal): return produce(node.type)
	if isinstance(node, Word): return tenv[node.val]
	if isinstance(node, Seq): return seqtype(node, tenv)
	if isinstance(node, Pipe): return pipetype(node, tenv)
	if isinstance(node, Block): return blocktype(node, tenv)
	if isinstance(node, Quote): return produce(blocktype(node, tenv))
	raise Exception("Unknown AST Node")
def typecheck(node, tenv):
	type = _typecheck(node, tenv)
	#print node, "\n\t", type, '\n'
	return type