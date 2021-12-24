#!/usr/bin/env python3

import re
import itertools
import sys
import functools
import z3
import string
import time

s = z3.Solver()

version = [z3.Int('version_%d' % i) for i in range(14)]
assert(len(version) == 14)

for i in range(14):
  s.add(version[i] > 0)
  s.add(version[i] <= 9)


class State:
  def __init__(self):
    self.values = {a: [z3.Int(a)] for a in 'wxyz'}

  def get_fresh_variable(self, reg):
    assert(reg in self.values)
    n = len(self.values[reg])
    v = z3.Int('%s_%d' % (reg, n))
    self.values[reg].append(v)
    return v

  def get_value(self, reg):
    assert(len(self.values[reg]) > 0)
    return self.values[reg][-1]

state = State()

version_nibble = 0
for line in sys.stdin.readlines():
  line = line.rstrip('\n')
  if not line: continue

  elms = line.split(' ')

  op = elms[0]
  if op == 'inp':
    aname = elms[1]
    anew = state.get_fresh_variable(aname)
    s.add(anew == version[version_nibble])
    version_nibble += 1
  elif op == 'add':
    (aname, bname) = (elms[1], elms[2])

    assert(aname in 'wxyz')
    aold = state.get_value(aname)
    anew = state.get_fresh_variable(aname)

    if bname in 'wxyz':
      bold = state.get_value(bname)
    else:
      bold = int(bname)

    s.add(anew == aold + bold)
  elif op == 'mul':
    (aname, bname) = (elms[1], elms[2])

    assert(aname in 'wxyz')
    aold = state.get_value(aname)
    anew = state.get_fresh_variable(aname)

    if bname in 'wxyz':
      bold = state.get_value(bname)
    else:
      bold = int(bname)

    s.add(anew == aold * bold)
  elif op == 'div':
    (aname, bname) = (elms[1], elms[2])

    assert(aname in 'wxyz')
    aold = state.get_value(aname)
    anew = state.get_fresh_variable(aname)

    if bname in 'wxyz':
      bold = state.get_value(bname)
    else:
      bold = int(bname)

    s.add(anew == aold / bold)
  elif op == 'mod':
    (aname, bname) = (elms[1], elms[2])

    assert(aname in 'wxyz')
    aold = state.get_value(aname)
    anew = state.get_fresh_variable(aname)

    if bname in 'wxyz':
      bold = state.get_value(bname)
    else:
      bold = int(bname)

    s.add(anew == aold % bold)
  elif op == 'eql':
    (aname, bname) = (elms[1], elms[2])

    assert(aname in 'wxyz')
    aold = state.get_value(aname)
    anew = state.get_fresh_variable(aname)

    if bname in 'wxyz':
      bold = state.get_value(bname)
    else:
      bold = int(bname)

    s.add(anew == z3.If(aold == bold, 1, 0))
  else:
    print('op %s is not supported' % op)
    sys.exit(1)

zold = state.get_value('z')
s.add(zold == 0)

print('[+] verifying satisfiability ...')

start = time.time()

solutions = set()
while s.check() == z3.sat:
  model = s.model()

  solution = 0
  for i in range(14):
    solution *= 10
    solution += model[version[i]].as_long()
  solutions.add(solution)

  remove = 'z3.Or('
  remove += ','.join(['version[%d] != %d' % (i, model[version[i]].as_long()) for i in range(14)])
  remove += ')'

  s.add(eval(remove))

  if len(solutions) % 100 == 0:
    print('current runtime %r, %d solutions' % (time.time()-start, len(solutions)))

print('')

print('took ', time.time()-start)
print(max(solutions))
print(min(solutions))
