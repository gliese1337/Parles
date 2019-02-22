from ParlesTypes import StackType, TypeVar, FuncType, genvar

def genstackc(p, q):
  ptop, qtop = p.top, q.top
  plen, qlen = len(ptop), len(qtop)
  if plen > qlen:
    ptop, qtop = qtop, ptop
    plen, qlen = qlen, plen
    p, q = q, p
  extra = qlen - plen
  etop = qtop[:extra] if extra else []
  loc = [(StackType(p.row,[]), StackType(q.row, etop))]         
  for np, nq in zip(ptop, qtop[extra:]):
    loc.extend(genc(np, nq))
  return loc


def genc(p, q):
  if p == q:
    return []
  if isinstance(p, TypeVar):
    return [(p, q)]
  if isinstance(q, TypeVar):
    return [(q, p)]
  if isinstance(p, FuncType) and isinstance(q, FuncType):
    return genstackc(p.input, q.input)+genstackc(p.output, q.output)
  if isinstance(p, StackType) and isinstance(q, StackType):
    return genstackc(p, q)
  raise Exception("Cannot constrain "+str(p)+" and "+str(q))


def subval(Z, sym, val):
  if isinstance(Z, TypeVar):
    return val if Z == sym else Z
  if isinstance(Z, StackType):
    return StackType(Z.row, map(lambda z: subval(z, sym, val), Z.top))
  if isinstance(Z, FuncType):
    return FuncType(subval(Z.input, sym, val), subval(Z.output, sym, val))
  return Z


def substack(Z, sym, val):
  if isinstance(Z, StackType):
    subfn = lambda z: substack(z, sym, val)
    if Z.row == sym.row:
      return StackType(val.row, val.top+map(subfn, Z.top))
    else:
      return StackType(Z.row, map(subfn, Z.top))
  if isinstance(Z, FuncType):
    return FuncType(substack(Z.input, sym, val), substack(Z.output, sym, val))
  return Z


def replacevars(sym, val, loc):
  if isinstance(sym, StackType):
    if len(sym.top) > 0:
      raise Exception("Can't substitute row variable with non-empty stack")
    if not isinstance(val, StackType):
      raise Exception("Can't substitute non-stack into row variable")
    subfn = lambda Z: substack(Z, sym, val)
  else:
    subfn = lambda Z: subval(Z, sym, val)
  return [(subfn(left), subfn(right)) for (left, right) in loc]


def occurs(sym, val):
  if isinstance(val, TypeVar):
    return sym == val
  if isinstance(val, FuncType):
    return occurs(sym, val.input) or occurs(sym, val.output)
  if isinstance(val, StackType):
    return any(occurs(sym, t) for t in val.top)
  return False


def unifyreplace(stack, subst, sym, val):
  if occurs(sym, val):
    raise Exception("Recursive type")
  stack = replacevars(sym, val, stack)
  subst = replacevars(sym, val, subst)+[(sym, val)]
  return stack, subst


def unify(stack):
  subst = []
  while len(stack) > 0:
    #print '\n',stack, subst
    c = stack.pop() # pop the constraint X = Y off the stack:
    X, Y = c
    if X == Y: continue
    elif isinstance(X, TypeVar):
      #print "Replace var",X,"with",Y
      stack, subst = unifyreplace(stack, subst, X, Y) # replace all occurrences of X by Y and add X = Y to the substitution.
    elif isinstance(Y, TypeVar):
      #print "Replace var",Y,"with",X
      stack, subst = unifyreplace(stack, subst, Y, X) # replace all occurrences of Y by X and add Y = X to the substitution.
    elif isinstance(X, StackType):
      if not isinstance(Y, StackType):
        raise Exception("Cannot unify "+str(Y)+" with non-stack type")
      if len(X.top) == 0:
        if X.row == Y.row:
          if len(Y.top) == 0:
            continue # If X and Y are identical, do nothing.
          raise Exception("Infinite Stack")
        #print "Replace stack",X,"with",Y
        stack, subst = unifyreplace(stack, subst, X, Y) # Otherwise, replace all occurrences of X by Y and add X = Y to the substitution.
      else:
        #print "Normalize",X,"and",Y
        stack += genstackc(X, Y) # Normalize X & Y
    elif isinstance(X, FuncType) and isinstance(Y, FuncType):
      #print "Equate",X,"and",Y
      stack += genstackc(X.input, Y.input)
      stack += genstackc(X.output, Y.output)
    else:
      raise Exception(str(X)+" and "+str(Y)+" do not unify")
  return subst


def _typevary(t, poly, vm, rm):
  def ref(h, v):
    return h[v] if v in h else v
  def refset(h, v):
    if v not in h:
      h[v] = genvar()
    return h[v]
  if isinstance(t, TypeVar):
    return (refset if poly else ref)(vm, t)
  if isinstance(t, StackType):
    row = (refset if poly else ref)(rm, t.row)
    top = map(lambda nt: _typevary(nt, poly, vm, rm), t.top)
    return StackType(row, top)
  if isinstance(t, FuncType):
    input = _typevary(t.input, poly, vm, rm)
    output = _typevary(t.output, poly, vm, rm) #_typevary(t.output, False, vm, rm)
    return FuncType(input, output)
  return t


def typevary(t):
  return _typevary(t, True, {}, {})


def subvar(Z, sym, val):
  if isinstance(Z, FuncType):
    return FuncType(subvar(Z.input, sym, val), subvar(Z.output, sym, val))
  if isinstance(Z, TypeVar)\
    and isinstance(sym, TypeVar)\
    and Z == sym:
    return typevary(val) if isinstance(val, FuncType) else val
  if isinstance(Z, StackType):
    r = lambda z: subvar(z, sym, val)
    if isinstance(sym, StackType)\
      and Z.row == sym.row:
      return StackType(val.row, map(r, val.top+Z.top))
    return StackType(Z.row, map(r, Z.top))
  return Z


def compose(f, g):
  f = typevary(f)
  input, output = f.input, g.output
  for (left, right) in unify(genstackc(f.output, g.input)):
    input = subvar(input, left, right)
    output = subvar(output, left, right)
  return FuncType(input, output)