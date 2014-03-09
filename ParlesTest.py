from ParlesParser import parse
from ParlesTypes import *
from ParlesCompiler import alphavary, typecheck, TypeEnv
from ParlesCompose import compose

env = TypeEnv().extend({
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

def printparse(prog):
	ast = alphavary(parse(prog))
	print '\n', ast
	print typecheck(ast, env)

printparse("""
+ 1 2;
"hi";
/% 7 3 | +;
{ a : num ->
	if < 1 2
		[print "true"]
		[print "false"]
	{ a : str -> print a }
};
""")

printparse("""
+ 1 2;
"hi";
/% 7 3 | +;
{ a : num b : str ->
	if < 1 2
		[print "true"]
		[print "false"]
	print b
};
""")

printparse("""
\\a : num + 1 2 "hi" 4;
{ b : str -> print b};
if < 1 a
	[print "true"]
	[print "false"]
""")

printparse("""
if < 1 2
	[print "true"]
	[print "false"]
""")