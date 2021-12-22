#!/usr/bin/env python3

import re
import sys
import functools
import operator
import numpy
import bisect

debug = True
debug = False

def parse_input():
  for line in sys.stdin.readlines():
    m = re.match(r'(off|on) x=(-?\d+)\.\.(-?\d+),y=(-?\d+)\.\.(-?\d+),z=(-?\d+)\.\.(-?\d+)', line)
    assert(m)
    elms = list(m.groups())
    elms[0] = False if elms[0] == 'off' else True
    for i in range(1, len(elms), 2):
      elms[i] = int(elms[i])
      elms[i+1] = int(elms[i+1])+1
    yield tuple(elms)

xvalues = set([-50,50])
yvalues = set([-50,50])
zvalues = set([-50,50])

boot_actions = [x for x in parse_input()]

for (toggle, x0, x1, y0, y1, z0, z1) in boot_actions:
  xvalues.add(x0)
  xvalues.add(x1)
  yvalues.add(y0)
  yvalues.add(y1)
  zvalues.add(z0)
  zvalues.add(z1)

state = numpy.full((len(xvalues)+1, len(yvalues)+1, len(zvalues)+1), False, dtype=bool)

xvalues = sorted(xvalues)
yvalues = sorted(yvalues)
zvalues = sorted(zvalues)

def convert_range(vals, start, end):
  assert(start in vals)
  assert(end in vals)
  i0 = bisect.bisect_left(vals, start)
  assert(start == vals[i0])
  i1 = bisect.bisect_left(vals, end)
  assert(end == vals[i1])
  return (i0, i1)

for (toggle, x0, x1, y0, y1, z0, z1) in boot_actions:
  (x0, x1) = sorted([x0, x1])
  (y0, y1) = sorted([y0, y1])
  (z0, z1) = sorted([z0, z1])
  print('turning %r to %r' % (((x0, x1), (y0, y1), (z0, z1)), toggle))

  (xi0, xi1) = convert_range(xvalues, x0, x1)
  (yi0, yi1) = convert_range(yvalues, y0, y1)
  (zi0, zi1) = convert_range(zvalues, z0, z1)

  for xi in range(xi0, xi1):
    for yi in range(yi0, yi1):
      for zi in range(zi0, zi1):
        if debug and state[xi][yi][zi] != toggle:
          print('turning %s' % ('off' if not toggle else 'on'))
          for xx in range(xvalues[xi], xvalues[xi+1]):
            for yy in range(yvalues[yi], yvalues[yi+1]):
              for zz in range(zvalues[zi], zvalues[zi+1]):
                print('  %d,%d,%d' % (xx, yy, zz))

        state[xi][yi][zi] = toggle

count = 0
for xi in range(len(xvalues)+1):
  print('processed x=%d cutter' % xi)
  for yi in range(len(yvalues)+1):
    for zi in range(len(zvalues)+1):
      if state[xi][yi][zi]:
        count += functools.reduce(operator.mul, [a[i+1]-a[i] for (a,i) in [(xvalues, xi), (yvalues, yi), (zvalues, zi)]])
print(count)
