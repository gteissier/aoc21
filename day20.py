#!/usr/bin/env python3

import itertools
import functools
import re
import sys


def load(d):
  with open(d) as f:
    algorithm = f.readline().rstrip('\n')
    assert(all(c in '.#' for c in algorithm))
    algorithm = algorithm.replace('.', '0').replace('#', '1')
    assert(len(algorithm) == 512)

    f.readline()

    img = []
    for line in f.readlines():
      line = line.rstrip('\n')
      img.append([c.replace('.', '0').replace('#', '1') for c in line])

    sparse = {}
    n = len(img)
    m = len(img[0])
    for i in range(n):
      for j in range(m):
        sparse[(i,j)] = img[i][j]

  return (algorithm, img, sparse)



def sq(spr, i, j, filler='0'):
  n = len(img)
  m = len(img[0])

  sq = ''
  for x in (-1, 0, 1):
    for y in (-1, 0, 1):
      if (x+i,y+j) in spr:
        sq += spr[(x+i,y+j)]
      else:
        sq += filler
  assert(len(sq) == 9)
  return sq

def enhance(algo, spr, filler, width=4):
  n = len(img)
  m = len(img[0])

  imx = max(i for (i,j) in spr)
  imn = min(i for (i,j) in spr)
  jmx = max(j for (i,j) in spr)
  jmn = min(j for (i,j) in spr)

  new_spr = {}
  for i in range(imn-width, imx+width):
    for j in range(jmn-width, jmx+width):
      level = int(sq(spr, i, j, filler), 2)
      new_spr[(i,j)] = algo[level]

  return new_spr

(algo, img, spr) = load(sys.argv[1])
for i in range(50):
  print(i)
  if i % 2 == 0: filler = '0'
  else: filler = '1'
  spr = enhance(algo, spr, filler=filler)

lit = 0
for ((i,j),p) in spr.items():
  if p == '1': lit += 1
print(lit)
