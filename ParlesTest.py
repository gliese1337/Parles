from ParlesCompiler import parse, typecheck, simplify, compile

def printparse(prog):
	try:
		ast = parse(prog)
		simpl = simplify(ast)
		print '\n', ast
		print simpl
		type, main, quots = compile(prog)
		print '\n',type
		print main
		print quots
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