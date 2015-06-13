Parles - A Paren-less Lisp (Sort Of)
=====

Parles is a concatenative programming language, like Factor, Joy, or FORTH. It is a common complaint among non-Lisp lovers that Lisps just have to darn many parentheses. It turns out, however, that if you're willing to introduce a minimal level of static typing into your Lisp (and disallow variadic functions), bracketing information can be fully recovered by the type system without needing to actually type any parentheses.

The current experimental implementation is done entirely in Python, running on a custom virtual machine, but the ultimate goal is to integrate with LLVM. The operational semantics were designed in Racket.

Parles still allows you to use parentheses if you want, for purposes of clarity. If parentheses are present, the type system will ensure that nothing _outside_ of the parentheses acts as an argument to anything _inside_ the parentheses. This means you can fully parenthesize your Parles code exactly like you would Scheme, and it will work just the same. If you want, however, you can leave any or all of them out, and just miss out on a little bit of extra type checking (you might run in to problems if you make a typo, but the type checker still manages to find a valid parenthesization that wasn't the one you had in mind!). Parles's parenthesization rules are much broader than Scheme's, though; if you like calling functions like `foo(a, b)` instead of `(foo a b)`, you go right ahead! The type system will just prevent you from doing something confusing like `(foo a) b`.

Because they ensure no outside data dependencies, parentheses in Parles can theoretically be used to indicate opportunities for automatic parallelism. This functionality is not currently implemented, and automatic bracket recovery through the type system could eventually allow for much more aggressive automatic parallelization, but interpreting programmer-written parens as parallelization annotations may be a useful step in improving Parles implementations.

Parentheses in Parles also delimit variable scopes. If you want to mark off scopes without opting-in to the type restrictions of parentheses, or if you just like the look of curly braces, you can use curly braces for that. Inspired by FORTH, square brackets (`[` and `]`) are used to delimit _quotes_- Parles's version of anonymous functions/closures.

Because of row type inference, there is never any need to declare the arguments to a function. Parles is very big on encouraging point-free style! Sometimes, though, you really need variable names for clarity, if nothing else; thus, all three block types (parens, curly braces, and square brackets) provide syntax for binding arguments to variables on entry to that scope. Observe the following two equivalent definitions of an anonymous function that adds together the quotient and modulus of two numbers:

    [x : num y : num -> + /% x y]
    [+ /%]

In the first case, the presence of the arrow keyword `->` indicates that everything before it should be interpreted as variable bindings ands type declarations. In the second case, the type system knows how many arguments the sum and divmod operators take, and will automatically construct the appropriate signature for the function. Declaring variables this way also allows you to break out of the absolutely-no-external-dependencies parenthesization rule. Because it requires arguments, `(+ /%)` will not typecheck. `(x : num y : num -> + /% x y)`, however, will. The reasoning here is that, while the language seems to be breaking its own rules by allowing you to make parens take arguments, it's not letting you take any _implicit_ arguments; any arguments to parens must be bound as variables, and we can actually desugar this to

    {x : num y : num -> (+ /% x y)}

These simple examples also demonstrate the ease with which Parles handles multivalue return. There is no need to use destructuring assignment to temporary variables, or `call-with-values`, or any other special construct; the multiple return values of `/%` automatically fill in both argument slots for `+`.

Sequencing Sugar
=====

These examples are also sufficient to demonstrate something interesting about Parles evaluation order, where the Lisp heritage really shines through even when you write in fully concatenative style. Most concatenative languages evaluate top-to-bottom and left-to-right; essentially, they end up with RPN arithmetic, familiar from HP calculators, but extending to all constructs, not just arithmetic operators.

Lisps, on the other hand (and just every other programming language), put the arguments to a function _after_ the name of the function. So, Parles does that same thing, to keep it looking familiar. This has the natural consequence, however, that Parles programs actually evaluate from _bottom to top_ and _right to left_. The right to left thing is no big deal within one line- it's exactly what we wanted- but bottom to top is a little weird. The simple fix would be to make line breaks significant, and re-order things base on line boundaries rather than treating Parles code as a single continous character stream that starts evaluation at the end. That, however, has ergonomic difficulties: you can no longer break up lines purely for formatting convenience. So, one way or another, we're going to need either an explicit "end-of-(logical, not necessarily formatted)-line" indicator or an explicit line continuation character (like Python's `\`) to control the order in which lines are executed and keep things sensible.

Parles handles this by means of the `;` sequencing operator. Within any given scope, a block of tokens occurring prior to a semicolon operator is moved to the end of the scope during parsing. When multiple semicolons are present in a single scope, this results in reversing the order of the semicolon-delimited blocks, while leaving token order unchanged within each block. By using curly braces and putting semicolons at the end of every line, you can make Parles look pretty much like a standard block-structured imperative Algol-family programming language.

The semicolon operator is purely syntactic sugar; reordering code by hand has exactly the same effect. Much like parens are a special kind of block with significance to the type system, Parles also has a type-sensitive sequencing construct: the pipe operator, `|`. Inspired by the Unix shell pipe, the pipe operator not only re-orders blocks of tokens, but ensures that the output type of the preceding block exactly matches the input type of the block following. While semicolons allow arbitrary unused arguments to "float" by on the concatenative stack, the pipe operator prevents this (at least as far as the effected blocks are concerned; the pipe operator does not enforce a completely empty data stack, and other code may have already placed things there that go ignored throughout the pipe).

The pipe operator can also be used to simulate infix operators. In situations where the pipe is not already delimited by semicolons (or other pipes) on both sides, it is necessary to use parens or curly braces to limit the scope of reordering. For example, the expression

    ((1 |+ 2) |* (3 |+ 4))

evaluates to `21`. What is actually going on is that the typechecker verifies that `1` produces a number while `+ 2` requires a number, similarly for `3` and `+ 4`, and for `(1 |+ 2)` and `* (3 |+ 4)`, and then performs re-ordering to produce

    (* (+ 4 3) (+ 2 1))

Uniform Call Syntax
=====

Parles has one more bit of more specialized sequencing sugar: the `.`, or method call, operator, which is used to simulate the dot-syntax method calls of OO languages like C++ or Java. Inspired by the D language's Uniform Function Call Syntax, it simply re-writes expressions of the form `bar.foo baz` to `foo bar baz`. Like the pipe, the `.` operator can also be used to simulate infix operations.

Also like the `|` operator, the `.` operator imposes some type restrictions: the receiver (whatever comes before the dot- the thing that you're calling a method on) must take no arguments and produce exactly one output, while the method call must take at last one argument (the receiver, self, or 'this' argument). Unlike the other sequencing operators, though, `.` comes with syntactic restrictions: it cannot occur at the beginning or end of a scope (i.e., there must be a receiver expression before it and a method to call after it, not a block or file boundary), and the method must be a single word, not a block, string, or any other expression. Violating those restrictions is a parse error.

The receiver, however, can be any arbitrary expression of the correct type, thus allowing for method chaining (i.e., `foo.bar(baz).qux(fred)`). The receiver is taken to be everything to the left of the `.` operator up to the last `;`, `|`, or opening block boundary. The re-writing action of the `.` operator can thus be simply described as moving a single word to its right leftwards to the last other sequencing operator or opening block boundary.

Non-Argument Variables
=====

In addition to binding arguments at the beginning of block scopes, Parles has special syntax for binding new variables at arbitrary positions. Binding expressions behave like functions which require one input and produce no outputs, and are written with a `\` followed immediately by a variable name (and type declaration). The scope of a variable binding extends over any code that executes after the binding in the same scope. If you only ever write variable bindings at the beginning of a line that ends with a semicolon, it's quite straightforward- the scope extends across all subsequent lines. In other cases, however, variable scope can become quite confusing given all of the re-ordering that may occur.

    {
        \greeting : str "hello";
        print greeting
    };
    print greeting _error -_ greeting _is out of scope here_

Variable bindings are desugared in the parser to curly-brace argument binding blocks. The above example is thus equivalent to

    {
        {   greeting : str ->
            print greeting
        } "hello";
        print greeting _error_
    }

In theory, Parles variables are immutable. However, they can be shadowed in lower scopes, which can look a lot like modification. For example,

    \word : str "Hello";
    print word;
    \word : str "Goodbye";
    print word;

is equivalent to

    {word : str ->
        print word;
        {word : str ->
            print word
        } "Goodbye";
    } "Hello";

Reassignments thus do not effect closure variables in higher scopes, and most likely will not occupy the same memory (though they may if the compiler can determine that usage of the two variables does not overlap).

Named Functions
=====

Parles has no special syntax for named functions; named functions are just quotes that have been bound to variables.

    \swap : (A any any -> A any any)
    [a : any b : any -> b a]

Function type signatures include an initial row type variable before the input and output types. These are necessary to include in order to indicate constraints on the types of related functions (like the arguments to `if`, described below). There is a great deal of redundancy in these kinds of declarations, but a future version of the language should make the variable binding type declaration optional.

For consistency with built-in functions like `print`, `+`, and `/%`, variables that hold function values will execute those functions whenever referenced. Thus, passing functions as arguments uniformly requires the use of quoting square brackets (or referencing a function which itself returns a function). We can thus write

    / swap 3 6

as an equivalent for

    / 6 3

In fact, as far as the type system is concerned, _all_ variables and constants are functions. Non-quote-valued variables are treated as constant functions which take no input, as are literal constant expressions.

Control Structures
=====

Parles uses quotes (with `[`square brackets`]`) for all delayed or skipped computation, not just producing anonymous functions. The `if` structure, for example, is implemented as a polymorphic function of three arguments: a boolean, a "then" quote, and an "else" quote.

    [hour : num ->
        if hour < 12 [
            print "Good Morning"
        ] [
            print "Good Afternoon"
        ]
    ]

The type of `if` is `(A bool (A -> B) (A -> B) -> B)`.
This could be implemented entirely inside the language, with a custom bool type constructed out of appropriate pair-selecting anonymous function values. While that would be rather inefficient, however, with two closures being generated every time the `if` construct is encountered even though only one of them will ever run, the compiler can recognize references to its built-in `if` function and inline all the code for closures that it knows cannot be called from any other location, resulting in compiled code no different from what you'd get out of a language with a special `if` keyword; this is similar to how the Java compiler handles intrinsic functions.

A future version of the language is planned to include support for continuations, to allow constructing arbitrary control structures in-language.