from ParlesAlphavary import alphavary
from ParlesAST import *

def _merge(node):
	if isinstance(node, Sequence):
		left, right = node
		nleft, args = _merge(left)
		if nleft == left: return node, []
		if isinstance(node, Seq): return Seq(nleft, right), args
		if isinstance(node, Pipe): return Pipe(nleft, right), args
	if isinstance(node, Quote): return node, []
	if isinstance(node, Scope):
		args, bnode = node
		nnode, nargs = _merge(bnode)
		if nnode == bnode: return bnode, args
		return nnode, args+nargs
	return node, []

def merge(node):
	if isinstance(node, Sequence):
		left, right = node
		nleft, nright = merge(left), merge(right)
		if left == nleft and right == nright: return node
		if isinstance(node, Seq): return Seq(nleft, nright)
		if isinstance(node, Pipe): return Pipe(nleft, nright)
	if isinstance(node, Scope):
		args, body = node
		nnode, nargs = _merge(body)
		if nnode == body: return node
		if isinstance(node, Block): return Block(args+nargs, nnode)
		if isinstance(node, Paren): return Paren(args+nargs, nnode)
		if isinstance(node, Quote): return Quote(args+nargs, nnode)
	return node

def simplify(node):
	return merge(alphavary(node))

def _flatten(node):
	"""returns (body, bound-in-scope, used)"""
	if isinstance(node, Word):
		return [node],[],set([node.val])
	if isinstance(node, Sequence):
		lnodes, lvars, lused = _flatten(node.left)
		rnodes, rvars, rused = _flatten(node.right)
		return lnodes+rnodes, lvars+rvars, lused|rused
	if isinstance(node, Quote):
		body, vars, used = _flatten(node.body)
		return [Func(node.args+vars,used,body)],[],used
	if isinstance(node, Scope):
		body, vars, used = _flatten(node.body)
		fullbody = map(lambda a: Pop(a.val,a.type), node.args)+body
		fullbound = node.args+vars
		return fullbody,fullbound,used
	return [node],[],set()

def flatten(node):
	body, vars, used = _flatten(node)
	return Func(vars, used, body)