from ParlesParser import parse
from ParlesSimplify import flatten, simplify
from ParlesCodegen import codegen
from ParlesBuiltins import typetable
from ParlesTypeChecker import typecheck, TypeEnv

topenv = TypeEnv().extend(typetable)

def compile(source):
	ast = parse(source)
	type = typecheck(ast,topenv)
	intermediate = flatten(simplify(ast))
	quots = codegen(intermediate)
	return type, quots

def link(quots):
	from ParlesStructs import Quotation, Instr
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