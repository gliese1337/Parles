from ParlesAST import *
from ParlesTypes import *
from ParlesCompose import compose

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

def methodtype(node, tenv):
	ltype = promote(typecheck(node.left, tenv))
	if len(ltype.input.top) > 0:
		raise Exception("Receiver expression cannot require arguments")
	if len(ltype.output.top) != 1:
		raise Exception("Receiver expression must produce a single output")

	rtype = promote(typecheck(node.right, tenv))
	if len(rtype.input.top) == 0:
		raise Exception("Method calls must take at least argument (the receiver)")

	return compose(ltype, rtype)

def blocktype(node, tenv):
	nenv = tenv.extend({a.val: a.type for a in node.args})
	(inrow, intop), output = typecheck(node.body, nenv)
	argtypes = list(reversed(map(lambda a: a.type, node.args)))
	return FuncType(StackType(inrow, intop+argtypes), output)

def parentype(node, tenv):
	nenv = tenv.extend({a.val: a.type for a in node.args})
	(inrow, intop), output = typecheck(node.body, nenv)
	if len(intop) > 0:
		raise Exception("Paren bodies cannot require arguments")
	argtypes = list(reversed(map(lambda a: a.type, node.args)))
	return FuncType(StackType(inrow, intop+argtypes), output)

def _typecheck(node, tenv):
	if isinstance(node, Literal): return produce(node.type)
	if isinstance(node, Word): return tenv[node.val]
	if isinstance(node, Seq): return seqtype(node, tenv)
	if isinstance(node, Pipe): return pipetype(node, tenv)
	if isinstance(node, Method): return methodtype(node, tenv)
	if isinstance(node, Paren): return parentype(node, tenv)
	if isinstance(node, Block): return blocktype(node, tenv)
	if isinstance(node, Quote): return produce(blocktype(node, tenv))
	if node is None:
		row = genvar()
		return FuncType(StackType(row,[]),StackType(row,[]))
	raise Exception("Unknown AST Node: "+str(node))

def typecheck(node, tenv):
	reset()
	type = _typecheck(node, tenv)
	return type