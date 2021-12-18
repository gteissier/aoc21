#!/usr/bin/env python3

import itertools
import sys

def walk(l, prefix=''):
  assert(type(l) == int or type(l) == list)
  if type(l) == int:
    yield (prefix, l)
  else:
    for x in walk(l[0], prefix+'l'):
      yield x
    for x in walk(l[1], prefix+'r'):
      yield x

def is_pair(x,y):
  if len(x) != len(y): return False
  return x[:-1] == y[:-1]


assert(is_pair('llr', 'lll'))
assert(not is_pair('llr', 'rll'))
assert(not is_pair('llr', 'l'))

class Snail:
  def __init__(self, l):
    self.content = {}

    for (prefix, value) in walk(l):
      self.content[prefix] = value

  def explode(self, path):
    # we have a pair made of two regulars
    assert(path + 'l' in self.content)
    assert(path + 'r' in self.content)

    keys = sorted(k for k in self.content.keys())
    vl = self.content[path + 'l']
    ndx = keys.index(path + 'l')
    if ndx != 0:
      self.content[keys[ndx-1]] += vl

    ndx = keys.index(path + 'r')
    vr = self.content[path + 'r']
    if ndx != len(keys)-1:
      self.content[keys[ndx+1]] += vr

    del self.content[path + 'l']
    del self.content[path + 'r']

    self.content[path] = 0

  def split(self, greater):
    value = self.content[greater]
    if value % 2 == 0:
      vl, vr = value//2, value//2
    else:
      vl, vr = value//2, value//2+1
    del self.content[greater]
    self.content[greater + 'l'] = vl
    self.content[greater + 'r'] = vr

  def reduce_once(self):
    # explode
    five_paths = sorted([k for k in self.content.keys() if len(k) == 5])
    # all paths are exactly 5
    for i in range(0, len(five_paths)-1):
      if is_pair(five_paths[i], five_paths[i+1]):
        self.explode(five_paths[i][:-1])
        return True

    # split
    greater = sorted([k for (k,v) in self.content.items() if v >= 10])
    if greater:
      self.split(greater[0])
      return True

    return False

  def reduce(self):
    while True:
      if not self.reduce_once():
        break

  def __add__(self, other):
    content = {}
    for (k, v) in self.content.items():
      content['l' + k] = v
    for (k, v) in other.content.items():
      content['r' + k] = v
    self.content = content
    self.reduce()
    return self

  def to_list(self):
    values = dict(self.content)
    while len(values) > 1:
      start = len(values)

      keys = sorted(values.keys())

      for i in range(len(keys)-1):
        if is_pair(keys[i], keys[i+1]):
          prefix = keys[i][:-1]
          assert(prefix not in values)

          values[prefix] = [values[keys[i]], values[keys[i+1]]]

          del values[keys[i]]
          del values[keys[i+1]]

          break
      assert(len(values) < start)

    return values['']

  def magnitude(self):
    values = dict(self.content)
    while len(values) > 1:
      start = len(values)

      keys = sorted(values.keys())

      for i in range(len(keys)-1):
        if is_pair(keys[i], keys[i+1]):
          prefix = keys[i][:-1]
          assert(prefix not in values)

          values[prefix] = 3*values[keys[i]] + 2*values[keys[i+1]]

          del values[keys[i]]
          del values[keys[i+1]]

          break
      assert(len(values) < start)

    return values['']

  def __repr__(self):
    return '%r' % (self.content)


s = Snail(eval('[[1,2],[[3,4],5]]'))
print(s.magnitude())
assert(s.magnitude() == 143)

exprs = []
for line in sys.stdin.readlines():
  line = line.rstrip('\n')
  exprs.append(line)

total = Snail(eval(exprs[0]))
for i in range(1, len(exprs)):
  total = total + Snail(eval(exprs[i]))
print(total.to_list())
print(total.magnitude())

all_sums = []
for p in itertools.permutations(range(len(exprs)), r=2):
  (i,j) = p
  si = Snail(eval(exprs[i]))
  sj = Snail(eval(exprs[j]))
  si += sj
  all_sums.append((i, j, si.magnitude()))

print(max(all_sums, key=lambda x: x[2]))
