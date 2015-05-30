#lang racket
(require redex)

(define-language parles
  [Binding (X Value)]
  [Env (env Binding ...)]
  [Stack (stack Value ...)]
  [Prog (Env Expr Stack)]
  [Args (X ...)]
  [Bool #t #f]
  [Op ! + - * > < =]
  [Proc Closure Block]
  [Callable Op Fn Bool Proc]
  [Word Callable Value X]
  [Fn (fn Args Stmnt ...)]
  [Closure (cls Env Args Stmnt ...)]
  [Block (block Args Stmnt ...)]
  [Scope block fn expr]
  [Stmnt Word (pop X)]
  [Expr (expr Word ...)]
  [Idem number]
  [Value Closure Bool Idem]
  [NVal Callable X]
  [C hole
     (Env hole Stack)
     (Env (expr Word ... C) Stack)]
  [(X Y) variable-not-otherwise-mentioned])

;TODO: Set up an explicit call stack so we're not nesting progs anymore

(define reduce
  (reduction-relation parles
   ;application rules
   (--> (Env (expr) (stack Value ...))
        (Value ...)
        "resolve")
   (--> (in-hole C (Scope Args ... Stmnt ... (pop X) Word ...))
        (in-hole C (Scope Args ... (block (X) Stmnt ...) Word ...))
        "scope")
   (--> (in-hole C (Scope (X ...) (block (Y ...) Stmnt ...)))
        (in-hole C (Scope (X ... Y ...) Stmnt ...))
        "merge")
   (--> (in-hole C (Env_1 (expr Word ... (Env_2 (expr) (stack Value_1 ...))) (stack Value_2 ...)))
        (in-hole C (Env_1 (expr Word ...) (stack Value_1 ... Value_2 ...)))
        "return")
   (--> (in-hole C (Env (expr Word ... NVal Value_1 Value_2 ...) (stack Value_3 ...)))
        (in-hole C (Env (expr Word ... NVal) (stack Value_1 Value_2 ... Value_3 ...)))
        "push")
   (--> (in-hole C (Env (expr Word ... (fn Args Stmnt ...)) (stack Value ...)))
        (in-hole C (Env (expr Word ...) (stack (cls Env Args Stmnt ...) Value ...)))
        "closure")
   (--> (in-hole C (Env (expr Word_1 Word_2 ... Proc) Stack))
        (in-hole C (Env (expr Word_1 Word_2 ... (call Env Stack Proc)) (stack)))
        "call")
   (--> (in-hole C (Env (expr Proc) Stack))
        (in-hole C (call Env Stack Proc))
        "tail")
   (--> (in-hole C (Env (expr Word ... Bool) Stack))
        (in-hole C (if Bool Env (expr Word ...) Stack))
        "if")
   (--> (in-hole C (Env (expr Word ... X) Stack))
        (in-hole C (lookup X Env (expr Word ...) Stack))
        "lookup")
   (--> (in-hole C (Env (expr Word ... Op) Stack))
        (in-hole C (delta Op Env (expr Word ...) Stack))
        "op")))

(define-metafunction parles
  [(dispatch Env Args Stack Stmnt ...)
   ((make-env Env Args Stack)
    (expr Stmnt ...)
    (pop-stack Args Stack))])

(define-metafunction parles
  [(call Env Stack (block Args Stmnt ...))
   (dispatch Env Args Stack Stmnt ...)]
  [(call Env_1 Stack (cls Env_2 Args Word ...))
   (dispatch Env_2 Args Stack Word ...)])

(define-metafunction parles
  [(lookup X (env) Expr Stack) ,(error "unbound variable")]
  [(lookup X (env Binding_1 ... (X Idem) Binding_2 ...) Expr (stack Value ...))
   ((env Binding_1 ... (X Idem) Binding_2 ...) Expr (stack Idem Value ...))]
  [(lookup X (env Binding_1 ... (X Callable) Binding_2 ...) (expr Word ...) Stack)
   ((env Binding_1 ... (X Callable) Binding_2 ...) (expr Word ... Callable) Stack)])

(define-metafunction parles
  [(make-env Env () Stack) Env]
  [(make-env (env Binding ...) (X Y ...) (stack Value_1 Value_2 ...))
   (make-env (env (X Value_1) Binding ...) (Y ...) (stack Value_2 ...))])

(define-metafunction parles
  [(pop-stack () Stack) Stack]
  [(pop-stack (X Y ...) (stack Value_1 Value_2 ...))
   (pop-stack (Y ...) (stack Value_2 ...))])

(define-metafunction parles
  [(if #t Env (expr Word ...) (stack Value_1 Value_2 Value_3 ...))
   (Env (expr Word ... Value_1) (stack Value_3 ...))]
  [(if #f Env (expr Word ...) (stack Value_1 Value_2 Value_3 ...))
   (Env (expr Word ... Value_2) (stack Value_3 ...))])

(define-metafunction parles
  [(delta ! Env Expr (stack Idem Value ...))
   (Env Expr (stack Idem Value ...))]
  [(delta ! Env (expr Word ...) (stack Callable Value ...))
   (Env (expr Word ... Callable) (stack Value ...))]
  [(delta + Env Expr (stack number_1 number_2 Value ...))
   (Env Expr (stack ,(+ (term number_1) (term number_2)) Value ...))]
  [(delta + Env Expr (stack number_1 number_2 Value ...))
   (Env Expr (stack ,(+ (term number_1) (term number_2)) Value ...))]
  [(delta - Env Expr (stack number_1 number_2 Value ...))
   (Env Expr (stack ,(- (term number_1) (term number_2)) Value ...))]
  [(delta * Env Expr (stack number_1 number_2 Value ...))
   (Env Expr(stack ,(* (term number_1) (term number_2)) Value ...))]
  [(delta < Env Expr (stack number_1 number_2 Value ...))
   (Env Expr (stack ,(< (term number_1) (term number_2)) Value ...))]
  [(delta > Env Expr (stack number_1 number_2 Value ...))
   (Env Expr (stack ,(> (term number_1) (term number_2)) Value ...))]
  [(delta = Env Expr (stack Value_1 Value_2 Value_3 ...))
   (Env Expr (stack ,(eq? (term Value_1) (term Value_2)) Value_3 ...))])

(test-predicate list? (redex-match parles
                                   (block Args Stmnt ... (pop X) Word ...)
                                   (term (block (b) + * a a (pop a) + 1 2 * b b))))

(test-predicate list? (redex-match parles
                                   (Env_1 (expr Word_1 ... (cls Env_2 Args Word_2 ...)) Stack)
                                   (term ((env) (expr (cls (env) (a) + 1 2)) (stack 3)))))
   
(test-predicate list? (redex-match parles
                                   (Scope Args ... Stmnt ... (pop X) Word ...)
                                   (term (expr * a a (pop a) + 1 2))))


#;(traces reduce
          (term ((env) (expr + 1 2) (stack))))

#;(traces reduce
          (term ((env) (expr ! (fn () + 1 2)) (stack))))

#;(traces reduce
          (term ((env) (expr ! (fn (a) + 1 2) 3) (stack))))

#;(traces reduce
          (term ((env) (expr ! (fn (a b) b a) 2 1) (stack))))

(traces reduce
          (term ((env) (expr (block (a) a) (fn (a b) + a b) 2 1) (stack))))

(traces reduce
          (term ((env) (expr * a a (pop a) + 1 2) (stack))))

(traces reduce
          (term ((env) (expr + * a a * b b (pop a) (pop b) + 1 2 + 4 5) (stack))))

(traces reduce
          (term ((env) (expr + * a a (pop a) * b b (pop b) + 1 2 + 4 5) (stack))))

(traces reduce
          (term ((env) (expr + * a a (pop a) + 1 2 * b b (pop b) + 4 5) (stack))))

#;(traces reduce
          (term ((env)
                 (expr (block (a) ! < 5 6 (fn () + a 1) (fn () + a 2)) 10)
                 (stack))))
#;(traces reduce
          (term ((env)
                 (expr (block (a) ! > 5 6 (fn () + a 1) (fn () + a 2)) 10)
                 (stack))))