from ParlesCompiler import parse, typecheck, simplify, compile, link
from ParlesVM import run

def printparse(prog):
	prog = prog.strip()
	try:
		print "Original:\n", prog
		ast = parse(prog)
		#print "AST:\t\t", ast
		ast = simplify(ast)
		print "\nSimplified:\n", ast

		type, quots = compile(prog)
		print "\nProg Type:\t", type
		entry, prog = link(quots)
		#for q in prog:
		#	print q,'\n'
		print "Running:"
		final = run(entry, prog)
		print "\nFinal Stack:", final
	except Exception as e:
		print e.message
	print '\n\n'

#printparse(r"""(+ 2)""")

printparse(
r"""
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

printparse(r"""
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

printparse(r"""
\a : num + 1 2 "hi" 4;
{ b : str -> print b};
if < 1 a
	[print "true"]
	[print "false"]
""")

printparse(r"""
if < 1 2
	[print "true"]
	[print "false"]
""")

printparse(r"""{x: num y: num -> / {x ;+ y} 2} 6 10""")
printparse(r"""{x: num y: num -> / {x ; {+ y}} 2} 6 10""")

printparse(r"""{x: num y: num -> / {x |+ y} 2} 6 10""")
printparse(r"""{x: num y: num -> / {x | {+ y}} 2} 6 10""")

printparse(r""""hi" | print; "bye" | print""")
printparse(r"""8 3 | /% ; 12 6 | /%""")
printparse(r"""8 3 ; /% ; 12 6 ; /%""")

printparse(r"""print "hello there" """)

printparse(r"""\average : (A num num -> A num) [x : num y : num -> / + x y 2]""")

printparse(r"""
\average : (A num num -> A num) [x : num y : num -> / + x y 2];
average 6 10
""")

printparse(r"""
\average : (num num -> num) [x : num y : num -> / + x y 2];
if < 1 2
	[print "true"]
	[print "false"];
average 6 10
""")