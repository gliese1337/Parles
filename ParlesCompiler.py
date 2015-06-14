from ParlesParser import parse
from ParlesSimplify import flatten, simplify
from ParlesCodegen import codegen
from ParlesBuiltins import typetable
from ParlesTypeChecker import typecheck, TypeEnv

topenv = TypeEnv().extend(typetable)

def compile(source):
	ast = simplify(parse(source))
	type = typecheck(ast,topenv)
	quots = codegen(flatten(ast))
	prog, entry = link(quots)
	return type, prog, entry

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
	return map(rewriteq, qlist), imap['main']

def serialize(prog, entry):
	return str(entry)+'\n'+'\n'.join(map(lambda q: q.serialize(), prog))

if __name__ == "__main__":
	import sys
	try:
		type, prog, entry = compile(sys.stdin)
		print serialize(prog, entry)
	except Exception as e:
		sys.stderr.write("Error: %s\n"%(e.message,))
