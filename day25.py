#!/usr/bin/env python3

import sys

m = []
for line in sys.stdin.readlines():
  m.append([c for c in line if c != '\n'])

def east(j,b):
  assert(j >= 0)
  assert(j < b)
  if j+1 < b: return j+1
  else: return 0

def south(i,a):
  assert(i >= 0)
  assert(i < a)
  if i+1 < a: return i+1
  else: return 0

def move(m):
  a = len(m)
  b = len(m[0])

  moving_east = []
  for i in range(a):
    for j in range(b):
      if m[i][j] == '>' and m[i][east(j,b)] == '.':
        moving_east.append((i,j))

  for (i,j) in moving_east:
    m[i][east(j,b)] = '>'
    m[i][j] = '.'

  moving_south = []
  for i in range(a):
    for j in range(b):
      if m[i][j] == 'v' and m[south(i,a)][j] == '.':
        moving_south.append((i,j))

  for (i,j) in moving_south:
    m[south(i,a)][j] = 'v'
    m[i][j] = '.'

  return moving_east or moving_south

def print_m(m):
  for r in m:
    print(''.join(r))

import itertools
for turn in itertools.count(1):
  if not move(m): break
print(turn)

