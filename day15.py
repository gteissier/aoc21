#!/usr/bin/env python3

import re
import networkx as nx
import sys

'''
we model the problem as a directional graph:
* each risk level is applied on entry, hence the risk level will be the weight on an edge terminating onto this node
* each node has at most four neighbours
* we add as many edges as neighbours, from self to neighbours, each weighted with neighbour risk level

we then apply networkx shortest_path to obtain the desired path

step 2 consists only in unfolding the initial risk levels five times in each direction before searching for the shortest path
'''

matrix = []
for line in sys.stdin.readlines():
  risks = [int(m.group(0)) for m in re.finditer(r'\d', line)]
  matrix.append(risks)

def neighbours(m, i, j):
  n = len(m)
  assert(n == len(m[0]))

  def valid(x,y):
    return x >= 0 and x < n and y >= 0 and y < n

  for (di, dj) in ((-1,0), (1,0), (0, -1), (0,1)):
    if valid(di+i, dj+j): yield (di+i, dj+j)

def weight(m, p):
  s = 0
  for n in p[1:]:
    (i,j) = n
    s += m[i][j]
  return s

def inc_and_wrap(x):
  x = x+1
  if x > 9: return 1
  else: return x

def times(m, k=5):
  n = len(m)
  assert(len(m[0]) == n)

  new_m = []
  for i in range(0, k*n):
    assert(i >= 0)
    row = []
    if i < n:
      for j in range(k*n):
        if j < n:
          row.append(m[i][j])
        else:
          row.append(inc_and_wrap(row[j-n]))
    else:
      for j in range(k*n):
        if j < n:
          row.append(inc_and_wrap(new_m[i-n][j]))
        else:
          row.append(inc_and_wrap(max([new_m[i-n][j], row[j-n]])))
    assert(len(row) == k*n)
    new_m.append(row)
  return new_m

def step1(m):
  G = nx.DiGraph()

  n = len(m)

  for i in range(n):
    for j in range(n):
      for (ni, nj) in neighbours(m, i, j):
        G.add_edge((i,j), (ni,nj), weight=m[ni][nj])

  path = nx.shortest_path(G, source=(0,0), target=(n-1,n-1), weight='weight')
  return weight(matrix, path)

print(step1(matrix))

def step2(m):
  G = nx.DiGraph()

  n = len(matrix)
  matrix5 = times(matrix, k=5)
  assert(len(matrix5) == 5*n)

  for i in range(5*n):
    for j in range(5*n):
      for (ni, nj) in neighbours(matrix5, i, j):
        G.add_edge((i,j), (ni,nj), weight=matrix5[ni][nj])

  path = nx.shortest_path(G, source=(0,0), target=(5*n-1,5*n-1), weight='weight')
  return weight(matrix5, path)

print(step2(matrix))
