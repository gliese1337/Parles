from ParlesTypes import *

class Quote():
	def __init__(self, args, body):
		self.type = None
		self.id = ""
		self.args = args
		self.body = body

	def __repr__(self):
		return "["+(' '.join(map(str,self.args))+" -> " if len(self.args) else "")+str(self.body)+"]"
		
class Block():
	def __init__(self, args, body):
		self.type = None
		self.id = ""
		self.args = args
		self.body = body

	def __repr__(self):
		return "{"+(' '.join(map(str,self.args))+" -> " if len(self.args) else "")+str(self.body)+"}"

class Word():
	def __init__(self,val):
		self.val = val
		self.type = None

	def __repr__(self):
		return self.val + (': ' + str(self.type) if self.type else "")

class Literal():
	def __init__(self,val,type):
		self.val = val
		self.type = type
		
	def __repr__(self):
		return str(self.val)
		
class Pipe():
	def __init__(self, left, right, id = ""):
		self.left = left
		self.right = right
		self.id = id
		self.type = None
		
	def __repr__(self):
		return "{"+str(self.left)+" | "+str(self.right)+"}"
		
class Seq():
	def __init__(self, left, right, id = ""):
		self.left = left
		self.right = right
		self.id = id
		self.type = None
		
	def __repr__(self):
		return str(self.right)+" "+str(self.left) #"(seq ("+str(self.left)+") ("+str(self.right)+"))"