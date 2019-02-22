from collections import namedtuple

class Scope():
  def __init__(self, args, body):
    self.type = None
    self.id = ""
    self.args = args
    self.body = body
    
  def __iter__(self):
    yield self.args
    yield self.body

def rep_scope(args, body):
  return (' '.join(map(str,args)) + " -> " if len(args) else "") \
      + (str(body) if body else "")

class Quote(Scope):
  def __repr__(self):
    return "["+rep_scope(self.args, self.body)+"]"

class Paren(Scope):
  def __repr__(self):
    return "("+rep_scope(self.args, self.body)+")"
    
class Block(Scope):
  def __repr__(self):
    return "{"+rep_scope(self.args, self.body)+"}"

class Word():
  def __init__(self,val,type=None):
    self.val = val
    self.type = type

  def __repr__(self):
    return self.val + (': ' + str(self.type) if self.type else "")

class Literal():
  def __init__(self,val,type=None):
    self.val = val
    self.type = type
    
  def __repr__(self):
    if self.type.val == 'str':
      return '"'+str(self.val)+'"'
    return str(self.val)

class Sequence():
  def __init__(self, left, right, id = ""):
    self.left = left
    self.right = right
    self.id = id
    self.type = None
    
  def __iter__(self):
    yield self.left
    yield self.right
  
class Pipe(Sequence):
  def __repr__(self):
    return "{"+str(self.left)+" | "+str(self.right)+"}"
    
class Seq(Sequence):
  def __repr__(self):
    return str(self.right)+" "+str(self.left)

class Method(Sequence):
  def __repr__(self):
    return "{"+str(self.left)+" ."+str(self.right)+"}"

Pop = namedtuple('Pop',['val','type'])
Func = namedtuple('Func',['vars','used','body'])