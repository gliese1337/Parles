from collections import defaultdict
from ParlesAST import Word, Sequence, Scope

class VarTable():
  def __init__(self,parent):
    self.parent = parent
    self.table = {}
    self.counts = defaultdict(int) if parent is None else parent.counts
  
  def __contains__(self,item):
    return (item in self.table) or (item in self.parent if self.parent else False)
  
  def __getitem__(self,index):
    if index in self.table:
      return self.table[index]
    if self.parent and (index in self.parent):
      return self.parent[index]
    return index
    
  def __setitem__(self,index,value):
    if index in self.table:
      raise Exception("Var Table Error")
    self.table[index] = value
    return value
  
  def genvar(self, index):
    count = self.counts[index]
    self.counts[index] += 1
    return index if count == 0 else index + str(count)

  def add(self,index):
    self[index] = self.genvar(index)
  
def _alphavary(node, vtable):
  if isinstance(node, Word):
    val = node.val
    if val in vtable:
      return Word(vtable[val],node.type)
    return node
  if isinstance(node, Sequence):
    left = _alphavary(node.left, vtable)
    right = _alphavary(node.right, vtable)
    return node.__class__(left, right)
  if isinstance(node, Scope):
    if len(node.args) > 0:
      nvtable = VarTable(vtable)
      for a in node.args:
        nvtable.add(a.val)
    else:
      nvtable = vtable
    args = map(lambda a: Word(nvtable[a.val],a.type), node.args)
    body = _alphavary(node.body, nvtable)
    return node.__class__(args, body)
  return node

def alphavary(node):
  return _alphavary(node, VarTable(None))