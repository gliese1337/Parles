from ParlesParser import parse
from ParlesSimplify import flatten, simplify
from ParlesCodegen import codegen
from ParlesTypes import *
from ParlesStructs import Quotation, Instr
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
	quots = codegen(intermediate)
	return type, quots

def link(quots):
	qlist = [q for k, q in quots.items()]
	imap = {q.id: i for i, q in enumerate(qlist)}
	def rewritei(instr):
		d, op, (m,i), a = instr
		if op == 'clos':
			return Instr(d, op, (m,imap[i]), a)
		return instr
	def rewriteq(q):
		id, rsize, vsize, instrs, ds = q
		return Quotation(id, rsize, vsize, map(rewritei, instrs), ds)
	return imap['main'], map(rewriteq, qlist)