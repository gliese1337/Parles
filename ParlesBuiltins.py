from ParlesTypes import *
from ParlesStructs import Instr
	
optable = {
	'+': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'add', (-1,0), (-1,1))],
	'-': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'sub', (-1,0), (-1,1))],
	'*': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'mul', (-1,0), (-1,1))],
	'/': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'div', (-1,0), (-1,1))],
	'<': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'lt', (-1,0), (-1,1))],
	'>': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'gt', (-1,0), (-1,1))],
	'=': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('r',1), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'eq', (-1,0), (-1,1))],
	'not': [Instr(('r',0), 'pop', (-3,0), (-3,0)),Instr(('s',0), 'not', (-1,0), (-3,0))],
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

typetable = {
	'+': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num')])),
	'-': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num')])),
	'*': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num')])),
	'/': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num')])),
	'/%': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num'), AtomType('num')])),
	'<': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('bool')])),
	'>': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('bool')])),
	'=': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('bool')])),
	'not': FuncType(StackType(TypeVar('a'), [AtomType('bool')]),
					StackType(TypeVar('a'), [AtomType('bool')])),
	'if': FuncType(	StackType(TypeVar('a'), [	FuncType(StackType(TypeVar('a'),[]),StackType(TypeVar('b'),[])),
												FuncType(StackType(TypeVar('a'),[]),StackType(TypeVar('b'),[])),
												AtomType('bool')]),
					StackType(TypeVar('b'),[])),
	'print': FuncType(StackType(TypeVar('a'), [AtomType('str')]), StackType(TypeVar('a'),[]))
}