from collections import defaultdict
from ParlesAST import *
from ParlesTypes import *

#Block, Quote, Pipe, Seq
def checkword(wrd):
	if wrd == '->': return ('ARG_ARROW',wrd)
	try:
		return ('NUMBER',int(wrd))
	except ValueError:
		return ('WORD',wrd)

def tokenize(input):
	stopchars = "[]{}()\\|:;."
	whitespace = " \t\r\n"
	wrd = ""
	strmode = False
	for c in input:
		if strmode:
			if c == '"':
				yield ('STRING',wrd)
				strmode = False
				wrd = ""
			else:
				wrd += c
		elif c in stopchars:
			if len(wrd):
				yield checkword(wrd)
				wrd = ""
			if c == '[': yield ('OPEN_QUOTE',c)
			elif c == ']': yield ('CLOSE_QUOTE',c)
			elif c == '(': yield ('OPEN_PAREN',c)
			elif c == ')': yield ('CLOSE_PAREN',c)
			elif c == '{': yield ('OPEN_BLOCK',c)
			elif c == '}': yield ('CLOSE_BLOCK',c)
			elif c == ';': yield ('SEQ',c)
			elif c == '|': yield ('PIPE',c)
			elif c == '.': yield ('METHOD',c)
			elif c == '\\': yield ('LAMBDA',c)
			elif c == ':': yield ('TYPE',c)
		elif c in whitespace:
			if len(wrd):
				yield checkword(wrd)
				wrd = ""
		elif c == '"':
			strmode = True
		else:
			wrd += c
	if strmode:
		raise Exception("Unclosed String")
	if len(wrd):
		yield checkword(wrd)

def safe_next(t):
	try:
		token = t.next()
	except StopIteration:
		token = ("EOF","EOF")
	return token

def args_body(tokenizer,checktype):
	body, (type, val) = parseLine(tokenizer)
	if type == 'ARG_ARROW':
		args = body
		for a in args:
			if a.type is None:
				raise Exception("Missing argument type for "+str(a))
		body, (type, val) = parseLine(tokenizer)
	else:
		args = []
	checktype(type)
	return args, body

def parseQuote(tokenizer):
	def checktype(type):
		if type != 'CLOSE_QUOTE':
			raise Exception("Missing closing bracket: '"+val+"'")
	args, body = args_body(tokenizer,checktype)
	return Quote(args,body), safe_next(tokenizer)

def parseParen(tokenizer):
	def checktype(type):
		if type != 'CLOSE_PAREN':
			raise Exception("Missing closing paren: '"+val+"'")
	args, body = args_body(tokenizer,checktype)
	return Paren(args,body), safe_next(tokenizer)

def parseBlock(tokenizer):
	def checktype(type):
		if type != 'CLOSE_BLOCK':
			raise Exception("Missing closing brace: '"+val+"'")
	args, body = args_body(tokenizer,checktype)
	return Block(args,body), safe_next(tokenizer)

def makeStack(l):
	if l[0].type is not None:
		raise Exception("Can't type row variable")
	for a in l[1:]:
		if a.type is None:
			raise Exception("Missing argument type for "+str(a))
	return StackType(TypeVar(l[0]),map(AtomType,l[1:]))

def parseStack(tokenizer):
	type, val = safe_next(tokenizer)
	if type != 'WORD':
		raise Exception("Missing Row Variable")
	rowvar = TypeVar(val)
	typelist = []
	type, val = safe_next(tokenizer)
	while True:
		if type == 'WORD':
			typelist.append(AtomType(val))
			type, val = safe_next(tokenizer)
		elif type == 'OPEN_PAREN':
			ftype, (type, val) = parseFunc(tokenizer)
			typelist.append(ftype)
		else:
			return StackType(rowvar, typelist), (type, val)

def parseFunc(tokenizer):
	t1, (type, val) = parseStack(tokenizer)
	if type != 'ARG_ARROW':
		raise Exception("Invalid type declaration")
	t2, (type, val) = parseStack(tokenizer)
	if type != 'CLOSE_PAREN':
		raise Exception("Invalid type declaration")
	return FuncType(t1, t2)

def parseType(tokenizer):
	type, val = safe_next(tokenizer)
	if type == 'WORD':
		return TypeName(val)
	if type == 'OPEN_PAREN':
		return parseFunc(tokenizer)
	raise Exception("Invalid type declaration: "+val)
	
def parseLambda(prefline, tokenizer):
	type, val = safe_next(tokenizer)
	if type != 'WORD':
		raise Exception("Missing lambda argument: "+val)
	arg = Word(val)
	
	type, val = safe_next(tokenizer)
	if type == 'TYPE':
		arg.type = parseType(tokenizer)
	
	rest, next = parseLine(tokenizer)
	if isinstance(rest, Seq):
		if prefline: body = Seq(prefline,rest.right)
		else: body = rest.right
		lblock = Block([arg],body)
		return Seq(rest.left, lblock), next
	else:
		lblock = Block([arg],prefline)
		return Seq(rest, lblock), next

def nodeify(line):
	if len(line) == 0:
		return None
	if len(line) == 1:
		return line[0]
	return Seq(line[-1],nodeify(line[:-1]))

def parseLine(tokenizer, next=None, stops=[]):
	close_types=['CLOSE_QUOTE', 'CLOSE_BLOCK', 'CLOSE_PAREN', 'EOF']
	line = []
	if next is None: next = safe_next(tokenizer)
	while True:
		type, val = next
		if (type in close_types) or (type in stops):
			return nodeify(line), next
		if type == 'ARG_ARROW':
			return line, next
		if type == 'WORD':
			line.append(Word(val))
			next = safe_next(tokenizer)
		if type == 'NUMBER':
			line.append(Literal(val,AtomType('num')))
			next = safe_next(tokenizer)
		if type == 'STRING':
			line.append(Literal(val,AtomType('str')))
			next = safe_next(tokenizer)
		elif type == 'OPEN_QUOTE':
			block, next = parseQuote(tokenizer)
			line.append(block)
		elif type == 'OPEN_PAREN':
			block, next = parseParen(tokenizer)
			line.append(block)
		elif type == 'OPEN_BLOCK':
			block, next = parseBlock(tokenizer)
			line.append(block)
		elif type == 'TYPE':
			if len(line) == 0:
				raise Exception("Nothing to type")
			line[-1].type = parseType(tokenizer)
			next = safe_next(tokenizer)
		elif type == 'LAMBDA':
			node, next = parseLambda(nodeify(line), tokenizer)
			line = [node]
		elif type == 'SEQ':
			right, next = parseLine(tokenizer)
			if len(line) == 0:
				line = right
			elif right is not None:
				line = [Seq(nodeify(line),right)]
		elif type == 'PIPE':
			right, next = parseLine(tokenizer, stops = ['SEQ', 'PIPE'])
			if len(line) == 0:
				line = right
			elif right is not None:
				line = [Pipe(nodeify(line),right)]
		elif type == 'METHOD':
			if len(line) == 0:
				raise Exception("Missing method receiver")
			m_token = safe_next(tokenizer)
			type, val = m_token
			if type != "WORD":
				raise Exception("Missing method name")
			line = [Method(nodeify(line),Word(val))]
			next = safe_next(tokenizer)

def parse(input):
	tokenizer = tokenize(input)
	seq, next = parseLine(tokenizer)
	return seq
