from collections import defaultdict, namedtuple
from ParlesAST import *
from ParlesTypes import *
from ParlesStructs import Quotation, Instr
	
class VarRecord():
	def __init__(self,level,type,captured,index=0):
		self.level = level
		self.index = index
		self.type = type
		self.captured = captured

class SymTable():
	def __init__(self,parent=None):
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
		
	def __setitem__(self,index,value):
		if index in self.table:
			raise Exception("Symbol Table Error")
		self.table[index] = value
		return value
	
	def extend(self,kv):
		ntable = SymTable(self)
		ntable.table.update(kv)
		return ntable

optable = {
	'+': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'add', (-1,0), (-1,1))],
	'<': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'lt', (-1,0), (-1,1))],
	'/%': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('n',0), 'dmod', (-1,0), (-1,1))],
	'if': [	Instr(('r',0), 'pop', (-3,0), (-3,0)),	#retrieve the boolean
			Instr(('r',1), 'pop', (-3,0), (-3,0)),	#retrieve the "if" closure
			Instr(('n',0), 'jz', (-1,0), (-2,3)),	#check the boolean, skipping to the "else" block if neecessary
			Instr(('n',0), 'pop', (-3,0), (-3,0)),	#discard the "else" closure"
			Instr(('n',0), 'call', (-1,1), (-3,0)),	#call the "if" closure"
			Instr(('n',0), 'jmp', (-2,2), (-3,0)),	#jump past "else" block
			Instr(('r',1), 'pop', (-3,0), (-3,0)),	#retrieve the "else" closure
			Instr(('n',0), 'call', (-1,1), (-3,0))	#call the "else" closure
		],
	'print': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('n',0), 'print', (-1,0), (-3,0))]
}
		
def genword(val, level, symtable):
	global optable
	if val in symtable:
		record = symtable[val] 
		mode = level - record.level if record.captured else -1
		if isinstance(record.type, FuncType): #call function
			return [Instr(('n',0), 'call', (mode,record.index), (-3,0))]
		else: #push value
			return [Instr(('s',0), 'mov', (mode,record.index), (-3,0))]
	#built-in operator
	return optable[val]

def capanalysis(fn):
	bound, used, body = fn
	cused = set()
	for (_,lowerused,_) in filter(lambda n: isinstance(n, Func), body):
		cused |= lowerused
	lused = used - cused
	locals = [a for a in bound if a.val in lused and a.val not in optable]
	captured = [a for a in bound if a.val in cused]
	return locals, captured

def lifeanalysis(nlist,locals):
	lset = {a.val for a in locals}
	ltable = {v:(float("inf"),0) for v in lset}
	for i,node in enumerate(nlist):
		if (isinstance(node, Word) or isinstance(node, Pop)) and node.val in lset:
			val = node.val
			min, max = ltable[val]
			if i < min:	min = i
			if i > max: max = i
			ltable[val] = (min,max)
	eqlist = []
	while len(lset) > 0:
		var = lset.pop()
		min, max = ltable[var]
		eqset = set([var])
		for v in lset:
			amin, amax = ltable[v]
			if amin < min or amax > max:
				eqset.add(v)
		lset -= eqset
		eqlist.append(eqset)
	return eqlist
	
def gensymtable(quot, level, symtable):
	bound, _, body = quot
	#variable capture analysis
	locals, captured = capanalysis(quot)
	#local variable lifetime analysis and get sets of non-overlapping variables
	eqlist = lifeanalysis(body,locals)
	
	#Assign display variable indices
	vtable = {a.val: VarRecord(level, a.type, True, index=i) for i,a in enumerate(captured)}
	
	#Assign local variable indices
	types = {a.val: a.type for a in locals}
	for i,eqset in enumerate(eqlist):
		ni = i+2
		for v in eqset: vtable[v] = VarRecord(level, types[v], False, index=ni)
	
	return len(locals), len(captured), symtable.extend(vtable)

qid = 0
def genqid():
	global qid
	qid += 1
	return "q%d"%(qid,)

def genquot(node, level, symtable):
	_, used, body = node
	
	#find the deepest higher scope level from which we are capturing variables
	#our variables will occupy the next lowest level
	highvars = {v for v in used if v in symtable}
	accesslevel = max(symtable[v].level for v in highvars) if len(highvars) > 0 else 0
	varlevel = accesslevel + 1
	
	#generate new symtable and get local allocation sizes
	lsize, csize, nsymtable = gensymtable(node, varlevel, symtable)
	#eliminate vacuous display levels
	nlevel = accesslevel if csize == 0 else varlevel
	skip = level-accesslevel
	
	id = genqid()
	instrs, lowerqs = _codegen(body, nlevel+1, nsymtable)
	lowerqs[id] = Quotation(id, lsize+2, csize, instrs, skip)
	return [Instr(('s',0), 'clos', (nlevel,id),(-3,0))], lowerqs

def gennode(node, level, symtable):
	if isinstance(node, Literal): #push value
		return [Instr(('s',0), 'mov', (-2, node.val), (-3,0))],{}
	if isinstance(node, Word):
		return genword(node.val, level, symtable),{}
	if isinstance(node, Pop):
		#since mutation is not implemented, we don't need to check the level
		#this is guaranteed to always be local
		if node.val not in symtable: #unused variable == drop
			return [Instr(('n',0), 'pop', (-3,0), (-3,0))],{}
		record = symtable[node.val]
		mode = 'v' if record.captured else 'r' #move to the captured variable display or registers
		return [Instr((mode,record.index), 'pop', (-3,0), (-3,0))],{}
	if isinstance(node, Func):
		bound, used, body = node
		
		#check special cases- re-use known quotations
		if len(bound) == 0:
			if len(body) == 0:
				#TODO: push the no-op function
				pass
			elif len(body) == 1:
				#check is we need to unwrap and push a quoted function
				bnode = body[0]
				if isinstance(bnode, Word):
					record = symtable[bnode.val]
					if isinstance(record.type, FuncType):
						mode = level - record.level if record.captured else -1
						return [Instr(('s',0), 'mov', (mode,record.index), (-3,0))],{}
		
		#generate a new quotation
		return genquot(node, level, symtable)
	else:
		print "node:", node
		raise Exception("Unknown node type")

def _codegen(nlist, level, symtable):
	code, qtable = [], {}
	if not isinstance(nlist, list):
		raise Exception("Can't codegen a non-list")
	for c,q in map(lambda n: gennode(n, level, symtable), nlist):
		code += c
		qtable.update(q)
	return code, qtable

def codegen(main):
	global qid
	qid = 0
	#TODO: linker needs to replace ids with indices for 'clos' opcodes
	lsize, csize, symtable = gensymtable(main, 1, SymTable())
	code, qtable = _codegen(main.body, 1, symtable)
	main = Quotation('main', lsize+2, csize, code, 0)
	qtable['main'] = main
	return qtable