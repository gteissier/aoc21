#!/usr/bin/env python3

import re
import sys
import itertools
import functools

class Probe:
  def __init__(self, vx, vy):
    self.vx = vx
    self.vy = vy
    self.x = 0
    self.y = 0

  def step(self):
    self.x += self.vx
    self.y += self.vy
    if self.vx > 0: self.vx -= 1
    elif self.vx < 0: self.vx += 1
    self.vy -= 1

(x0, x1, y0, y1) = [int(m.group(1)) for m in re.finditer(r'(-?\d+)', sys.stdin.read())]
(x0, x1) = sorted([x0, x1])
(y0, y1) = sorted([y0, y1])

def acquired(p):
  return p.x >= x0 and p.x <= x1 and p.y >= y0 and p.y <= y1

y_mx = max([abs(y0), abs(y1)])

win = set()
for vx in range(1, x1+1):
  for vy in range(-y_mx-1, y_mx+1):
    p = Probe(vx, vy)
    y_max = None
    for c in itertools.count():
      p.step()
      if y_max is not None:
        if p.y > y_max: y_max = p.y
      else:
        y_max = p.y

      if acquired(p):
        win.add((vx, vy, y_max))
        break
      if p.x > x1 or p.y < y0:
        break

print(max(win, key=lambda x: x[2]))
print(len(win))
