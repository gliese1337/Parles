from collections import defaultdict, namedtuple
from ParlesAST import Func, Word, Pop, Literal
from ParlesTypes import FuncType
from ParlesStructs import Quotation, Instr
from ParlesBuiltins import optable

class VarRecord():
  def __init__(self,level,type,captured,index=0):
    self.level = level
    self.index = index
    self.type = type
    self.captured = captured

  def __repr__(self):
    return str((self.level, self.index, self.type, self.captured))

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

def lifeanalysis(nlist,locals): #currently broken
  lset = {a.val for a in locals}
  #calculate usage ranges
  max = len(nlist)
  ltable = {v:(max,0) for v in lset}
  for i,node in enumerate(nlist):
    if (isinstance(node, Word) or isinstance(node, Pop)) and node.val in lset:
      val = node.val
      min, max = ltable[val]
      if i < min:  min = i
      if i > max: max = i
      ltable[val] = (min,max)
  #calculate equivalence sets from non-overlapping ranges
  eqlist = []
  while len(lset) > 0:
    var = lset.pop()
    min, max = ltable[var]
    isdisjoint = lambda amin, amax: amax < min or amin > max
    eqset = {v for v in lset if isdisjoint(*ltable[v])}|set([var])
    lset -= eqset
    eqlist.append(eqset)
  return eqlist

def gensymtable(quot, level, symtable):
  bound, _, body = quot
  #variable capture analysis
  locals, captured = capanalysis(quot)

  #local variable lifetime analysis
  #finds sets of non-overlapping variables
  #eqlist = lifeanalysis(body,locals)
  eqlist = [set([a.val]) for a in locals]

  #Assign display variable indices
  vtable = {a.val: VarRecord(level, a.type, True, index=i) for i,a in enumerate(captured)}

  #Assign local variable indices
  types = {a.val: a.type for a in locals}
  for i,eqset in enumerate(eqlist):
    ni = i+2
    for v in eqset: vtable[v] = VarRecord(level, types[v], False, index=ni)

  return len(eqlist), len(captured), symtable.extend(vtable)

def optimize(instrs):
  before, after = float("inf"), len(instrs)
  while before > after:
    before = after
    last = instrs
    instrs, skip = [], set()
    for i, instr in enumerate(last):
      if i in skip: continue
      written = False
      ((spec,_), op, a1, a2) = instr
      if op == 'mov' and spec == 's':
        overwrites = set()
        for j, (dest, op2, _, _) in enumerate(last[i+1:], start=i+1):
          if op2 == 'mov':
            overwrites.add(dest)
            if dest[0] == 's': break
          elif op2 == 'pop':
            if dest not in overwrites:
              skip.add(j)
              instrs.append(Instr(dest, 'mov', a1, a2))
              written = True
            break
      if not written:
        instrs.append(instr)
    after = len(instrs)
  return instrs

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
  instrs = optimize(instrs)
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
    bound, _, body = node

    #check special cases- re-use known quotations
    if len(bound) == 0:
      if len(body) == 0:
        #TODO: push the no-op function
        pass
      elif len(body) == 1:
        #check if we need to unwrap and push a quoted function
        bnode = body[0]
        if isinstance(bnode, Word):
          record = symtable[bnode.val]
          if isinstance(record.type, FuncType):
            mode = level - record.level if record.captured else -1
            return [Instr(('s',0), 'mov', (mode,record.index), (-3,0))],{}

    #generate a new quotation
    return genquot(node, level, symtable)
  else:
    print("node:", node)
    raise Exception("Unknown AST Node Type")

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
  lsize, csize, symtable = gensymtable(main, 1, SymTable())
  code, qtable = _codegen(main.body, 1, symtable)
  main = Quotation('main', lsize+2, csize, code, 0)
  qtable['main'] = main
  return qtable