from ParlesParser import parse
from ParlesSimplify import flatten, simplify
from ParlesCodegen import codegen
from ParlesTypes import *
from ParlesTypeChecker import typecheck, TypeEnv

topenv = TypeEnv().extend({
	'+': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num')])),
	'/%': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('num'), AtomType('num')])),
	'<': FuncType(	StackType(TypeVar('a'), [AtomType('num'), AtomType('num')]),
					StackType(TypeVar('a'), [AtomType('bool')])),
	'if': FuncType(	StackType(TypeVar('a'), [	FuncType(StackType(TypeVar('a'),[]),StackType(TypeVar('b'),[])),
												FuncType(StackType(TypeVar('a'),[]),StackType(TypeVar('b'),[])),
												AtomType('bool')]),
					StackType(TypeVar('b'),[])),
	'print': FuncType(StackType(TypeVar('a'), [AtomType('str')]), StackType(TypeVar('a'),[]))
})

def compile(source):
	ast = parse(source)
	type = typecheck(ast,topenv)
	intermediate = flatten(simplify(ast))
	main, quots = codegen(intermediate)
	return type, main, quots
