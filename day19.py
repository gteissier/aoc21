#!/usr/bin/env python3

import re
import sys
import functools
import itertools
import networkx as nx

def gen_scanners(d):
  with open(d) as f:
    scanner = None
    beacons = []

    for line in f.readlines():
      line = line.rstrip('\n')
      if not line:
        yield (scanner, tuple(beacons))
        scanner = None
        beacons = []
      else:
        if not scanner:
          m = re.match(r'--- (.*) ---', line)
          assert(m)
          scanner = m.group(1)
        else:
          beacons.append(tuple(int(m.group(1)) for m in re.finditer(r'(-?\d+)', line)))

    yield (scanner, tuple(beacons))



@functools.lru_cache
def get_rotx():
  rots = []
  for (s,c) in [(0,1),(0,-1),(1,0),(-1,0)]:
    rots.append([[1,0,0],[0,c,-s],[0,s,c]])
  return rots

@functools.lru_cache
def get_roty():
  rots = []
  for (s,c) in [(0,1),(0,-1),(1,0),(-1,0)]:
    rots.append([[c,0,s],[0,1,0],[-s,0,c]])
  return rots

def get_rotz():
  rots = []
  for (s,c) in [(0,1),(0,-1),(1,0),(-1,0)]:
    rots.append([[c,-s,0],[s,c,0],[0,0,1]])
  return rots



def mat_mul(a,b):
  assert(len(a) == 3)
  assert(len(b) == 3)

  m = []
  m.append([0 for i in range(3)])
  m.append([0 for i in range(3)])
  m.append([0 for i in range(3)])
  for i in range(3):
    for j in range(3):
      m[i][j] = sum(a[i][k]*b[k][j] for k in range(3))
  return m

@functools.lru_cache(maxsize=None)
def get_rotations():
  rotations = set()
  for rx in get_rotx():
    for ry in get_roty():
      for rz in get_rotz():
        m = functools.reduce(mat_mul, [rx, ry, rz])

        m[0] = tuple(m[0])
        m[1] = tuple(m[1])
        m[2] = tuple(m[2])
        m = tuple(m)

        rotations.add(m)
  return rotations

rotations = get_rotations()
assert(len(rotations) == 24)


def dot_matrix(m, p):
  return tuple(sum(m[i][j]*p[j] for j in range(3)) for i in range(3))

def add(p, delta):
  return tuple(p[i]+delta[i] for i in range(3))

def dist(a,b):
  return sum(abs(a[i]-b[i]) for i in range(3))

scanners = [beacons for (name, beacons) in gen_scanners(sys.argv[1])]

def correlate(b1, b2):
  for r in get_rotations():
    rb2 = [dot_matrix(r, b) for b in b2]
    for (i1, i2) in itertools.product(range(len(b1)), range(len(b2))):
      delta = tuple([b1[i1][k]-rb2[i2][k] for k in range(3)])

      matched = []
      for b in rb2:
        if add(delta, b) in b1:
          matched.append(b)
      if len(matched) >= 12:
        return (r, delta)

to_match = [x for x in range(1, len(scanners))]
matched = [0]
transforms = {}

while to_match:

  processed = False
  for i in to_match:
    for j in matched:
      ret = correlate(scanners[j], scanners[i])
      if ret:
        (r, delta) = ret

        print('  correlated scanner %d to scanner %d' % (i, j))

        transforms[i] = (j, lambda x,r=r,delta=delta: add(delta, dot_matrix(r, x)))
        to_match.remove(i)
        matched.append(i)

        processed = True
        break
    if processed: break

def back_to_scanner_0(k):
  ops = [lambda x: x]
  while k != 0:
    assert(k in transforms)
    (j, op) = transforms[k]
    k = j
    ops.append(op)

  def apply(x):
    for op in ops:
      x = op(x)
    return x

  return apply

beacons_map = set()
centers = {}

for i in range(len(scanners)):
  t = back_to_scanner_0(i)
  assert(t)
  centers[i] = t((0,0,0))

  for b in scanners[i]:
    beacons_map.add(t(b))

print(len(beacons_map))

distances = []
for (i,j) in itertools.combinations(range(len(scanners)), r=2):
  distances.append((i,j,dist(centers[i], centers[j])))

print(max(distances, key=lambda x: x[2]))
