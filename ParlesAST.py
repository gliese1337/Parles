from ParlesTypes import *

class Scope():
	def __init__(self, args, body):
		self.type = None
		self.id = ""
		self.args = args
		self.body = body
		
	def __iter__(self):
		yield self.args
		yield self.body

class Quote(Scope):
	def __repr__(self):
		return "["+(' '.join(map(str,self.args))+" -> " if len(self.args) else "")+str(self.body)+"]"

class Paren(Scope):
	def __repr__(self):
		return "("+(' '.join(map(str,self.args))+" -> " if len(self.args) else "")+str(self.body)+")"
		
class Block(Scope):
	def __repr__(self):
		return "{"+(' '.join(map(str,self.args))+" -> " if len(self.args) else "")+str(self.body)+"}"

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

Pop = namedtuple('Pop',['val','type'])
Func = namedtuple('Func',['vars','used','body'])