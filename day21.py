#!/usr/bin/env python3

from collections import defaultdict
from itertools import product

starts = [4, 8]
starts = [7, 3]

p1_universes = {(starts[0],0): 1}
p2_universes = {(starts[1],0): 1}

def wrap(x):
  while x > 10:
    x -= 10
  return x

epochs = {}

epochs[0] = (p1_universes, p2_universes)

winning_p1 = 0
winning_p2 = 0
epoch = 0
while True:
  next_p1_universes = defaultdict(int)
  next_p2_universes = defaultdict(int)

  # compute epoch+1 possible universes for each player
  for ((c, s), n) in p1_universes.items():
    for roll in product(range(1, 4), repeat=3):
      d = sum(roll)
      next_c = wrap(c + d)
      assert(next_c in range(1, 11))
      next_s = s + next_c
      next_p1_universes[(next_c,next_s)] += n
  assert(all(c in range(1, 11) for (c,s) in next_p1_universes))
  assert(all(s >= 0 for (c,s) in next_p1_universes))

  for ((c, s), n) in p2_universes.items():
    for roll in product(range(1, 4), repeat=3):
      d = sum(roll)
      next_c = wrap(c + d)
      assert(next_c in range(1, 11))
      next_s = s + next_c
      next_p2_universes[(next_c,next_s)] += n
  assert(all(c in range(1, 11) for (c,s) in next_p2_universes))
  assert(all(s >= 0 for (c,s) in next_p2_universes))

  # game rule: when a player reaches 21, the game is over
  # when a tie occurs, player 1 which moves first wins
  # beware the glitch: we need to take p2 last turn values: p2_universes
  p2_total = sum([n2 for ((c,s),n2) in p2_universes.items() if s < 21])
  keys = list(next_p1_universes.keys())
  for (c,s) in keys:
    if s >= 21:
      n = next_p1_universes[(c,s)]
      winning_p1 += n*p2_total

  p1_total = sum([n1 for ((c,s),n1) in next_p1_universes.items() if s < 21])
  keys = list(next_p2_universes.keys())
  for (c,s) in keys:
    if s >= 21:
      n = next_p2_universes[(c,s)]
      winning_p2 += n*p1_total

  # update and break if all epochs have been processed
  keys = list(next_p1_universes.keys())
  for (c,s) in keys:
    if s >= 21:
      del next_p1_universes[(c,s)]

  keys = list(next_p2_universes.keys())
  for (c,s) in keys:
    if s >= 21:
      del next_p2_universes[(c,s)]

  epoch += 1
  p1_universes = next_p1_universes
  p2_universes = next_p2_universes
  epochs[epoch] = (p1_universes, p2_universes)

  if len(p1_universes) == 0 and len(p2_universes) == 0:
    break

print(max([winning_p1, winning_p2]))
