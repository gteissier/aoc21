#!/usr/bin/env python3

import itertools
import sys

def walk(l, prefix=''):
  '''generate all (path, regular) for a given list'''
  assert(type(l) == int or type(l) == list)
  if type(l) == int:
    yield (prefix, l)
  else:
    for x in walk(l[0], prefix+'l'):
      yield x
    for x in walk(l[1], prefix+'r'):
      yield x

def is_pair(x,y):
  '''pathx and pathy designate a pair iff pathx and pathy overlap except for the last component'''
  if len(x) != len(y): return False
  return x[:-1] == y[:-1]


assert(is_pair('llr', 'lll'))
assert(not is_pair('llr', 'rll'))
assert(not is_pair('llr', 'l'))

class Snail:
  '''Snail are just a collection of (path, regular) tuples
  We use a dictionary, with path as key
  '''
  def __init__(self, l):
    self.content = {}

    for (prefix, value) in walk(l):
      self.content[prefix] = value

  def explode(self, path):
    # we have a pair made of two regulars
    assert(path + 'l' in self.content)
    assert(path + 'r' in self.content)

    # several things to know here:
    # sorted uses lexicographic order for string: l < lr < r
    # if we sort paths, and find our path inside
    # we have the prev and the next (possibly)
    # and they coincide with the elements we want to update
    keys = sorted(k for k in self.content.keys())
    vl = self.content[path + 'l']
    ndx = keys.index(path + 'l')
    if ndx != 0:
      self.content[keys[ndx-1]] += vl

    ndx = keys.index(path + 'r')
    vr = self.content[path + 'r']
    if ndx != len(keys)-1:
      self.content[keys[ndx+1]] += vr

    # cut the old nodes
    del self.content[path + 'l']
    del self.content[path + 'r']

    # add a new node with value 0
    self.content[path] = 0

  def split(self, greater):
    value = self.content[greater]
    if value % 2 == 0:
      vl, vr = value//2, value//2
    else:
      vl, vr = value//2, value//2+1
      
    # cut old node
    del self.content[greater]
    
    # add two child nodes with computed values
    self.content[greater + 'l'] = vl
    self.content[greater + 'r'] = vr

  def reduce_once(self):
    # explode
    # to find level 4 pairs, we find regulars at level 5
    five_paths = sorted([k for k in self.content.keys() if len(k) == 5])
    # and find the first pair
    # sorted ensures we have the leftmost one (again lexicographic order)
    for i in range(0, len(five_paths)-1):
      if is_pair(five_paths[i], five_paths[i+1]):
        self.explode(five_paths[i][:-1])
        return True

    # split
    # find path for regulars whose values is greater or equal to ten
    greater = sorted([k for (k,v) in self.content.items() if v >= 10])
    if greater:
      # sorted ensure we have the leftmost one (again lexicographic order)
      self.split(greater[0])
      return True

    return False

  def reduce(self):
    '''reduce step by step until not possible'''
    while True:
      if not self.reduce_once():
        break

  def __add__(self, other):
    '''to create a new tree, we prefix existing paths with 'l' or 'r''''
    content = {}
    for (k, v) in self.content.items():
      content['l' + k] = v
    for (k, v) in other.content.items():
      content['r' + k] = v
    self.content = content
    self.reduce()
    return self

  def to_list(self):
    '''crappy: we build values from bottom, pair by pair. Yet it works'''
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
    '''the same, but evaluates the tree w.r.t. to magnitude'''
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


# verify magnitude works
s = Snail(eval('[[1,2],[[3,4],5]]'))
print(s.magnitude())
assert(s.magnitude() == 143)


# capture snail expressions
exprs = []
for line in sys.stdin.readlines():
  line = line.rstrip('\n')
  exprs.append(line)

# sum up snails
total = Snail(eval(exprs[0]))
for i in range(1, len(exprs)):
  total = total + Snail(eval(exprs[i]))
print(total.to_list())
print(total.magnitude())

# perform all r=2 permutations and get the maximum magnitude
all_sums = []
for p in itertools.permutations(range(len(exprs)), r=2):
  (i,j) = p
  si = Snail(eval(exprs[i]))
  sj = Snail(eval(exprs[j]))
  si += sj
  all_sums.append((i, j, si.magnitude()))

print(max(all_sums, key=lambda x: x[2]))
