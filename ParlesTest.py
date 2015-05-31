from ParlesCompiler import compile, serialize
from ParlesVM import run, load

def printparse(prog):
	prog = prog.strip()
	try:
		print "Program:\n\n", prog

		type, prog, entry = compile(prog)
		print "\nProg Type:\t", type

		#test seriaizing and reloading
		serial = serialize(prog, entry)
		prog, entry = load(l for l in serial.split('\n'))

		print "Output:"
		final = run(prog, entry)
		print "\nFinal Stack:", final
	except Exception as e:
		print e.message
	print '\n\n'

printparse(r"""(+ 2)""")

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