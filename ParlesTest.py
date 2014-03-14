from ParlesCompiler import parse, typecheck, simplify, compile, link
from ParlesVM import run

def printparse(prog):
	try:
		ast = parse(prog)
		print '\n', ast
		type, quots = compile(prog)
		print '\n', type
		entry, prog = link(quots)
		#for q in prog:
		#	print q,'\n'
		print "Running:"
		print run(entry, prog)
	except Exception as e:
		print e.message

		
printparse("""(+ 2)""")

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

printparse("""{x : num y : num -> / {x |{+ y}} 2} 6 10""")
printparse("""{x : num y : num -> / {x |+ y} 2} 6 10""")

#printparse("""
"""\\average : (num num -> num) [x : num y : num -> / + x y 2];
if < 1 2
	[print "true"]
	[print "false"];
average 6 10
"""
