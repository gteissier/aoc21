#!/usr/bin/env python3

import re
import sys
import itertools
import networkx
import pdb


line = sys.stdin.readline()
assert(line == '#############\n')
line = sys.stdin.readline()
assert(line == '#...........#\n')

stacks = [[] for _ in range(4)]

line = sys.stdin.readline()
for (i, rank) in enumerate([ord(c)-ord('A') for c in line if c in 'ABCD']):
  stacks[i].append((rank, False))

# step2: append extra layers
for (i, rank) in enumerate([3, 2, 1, 0]):
  stacks[i].append((rank, False))
for (i, rank) in enumerate([3, 1, 0, 2]):
  stacks[i].append((rank, False))

line = sys.stdin.readline()
for (i, rank) in enumerate([ord(c)-ord('A') for c in line if c in 'ABCD']):
  stacks[i].append((rank, False))

line = sys.stdin.readline()
assert(line == '  #########\n')

'''
state:
  * elements in the hallway, 11 places, only 7 legit
  * rooms

each amphipod is modelled as:
  * final_room
  * has_stopped
  * has_moved
'''

# other places are in front of a room, which is not a place we can stop
LEGIT_HALLWAY_PLACES =	(0, 1, 3, 5, 7, 9, 10)
STACK_PLACES = 		(     2, 4, 6, 8)
ENERGY = (1, 10, 100, 1000)

def possible_locs_out_of_room(i, hallway):
  assert(i in range(4))
  i = STACK_PLACES[i]

  k = i
  assert(hallway[k] is None)
  while k > 0:
    if hallway[k-1] is not None: break
    k -= 1
  mn = k

  k = i
  assert(hallway[k] is None)
  while k < 10:
    if hallway[k+1] is not None: break
    k += 1
  mx = k

  return (mn, mx)

initial_state = (
  tuple([None for i in range(11)]), 
  tuple([tuple(stacks[i]) for i in range(4)]),
)


def children_states(state):
  (hallway, rooms) = state

  # amphipods in the hallway that have stopped
  # they must go to their final destination: a[0]


  for (i, a) in enumerate(hallway):
    if a is None: continue

    (final, has_stopped) = a
    assert(has_stopped)
    assert(i != STACK_PLACES[final])
    if len(rooms[final]) == 4: continue
    if i > STACK_PLACES[final]:
      if any(c is not None for c in hallway[STACK_PLACES[final]:i-1]): continue

      new_hallway = list(hallway)
      new_hallway[i] = None
      energy = abs(STACK_PLACES[final]-i)
      assert(len(new_hallway) == 11)

      new_room = list(rooms[final])
      new_room.insert(0, a)

      # len(rooms[final]) == 0 <=> energy += 4
      # len(rooms[final]) == 3 <=> energy += 1
      energy += (4 - len(rooms[final]))

      new_room = tuple(new_room)
      assert(len(new_room) <= 4)

      new_state = (tuple(new_hallway), tuple([rooms[j] if j != final else new_room for j in range(4)]))
      yield (new_state, energy*ENERGY[final])
    else:
      if any(c is not None for c in hallway[i+1:STACK_PLACES[final]]): continue

      new_hallway = list(hallway)
      new_hallway[i] = None
      energy = abs(STACK_PLACES[final]-i)
      assert(len(new_hallway) == 11)

      new_room = list(rooms[final])
      new_room.insert(0, a)
      energy += (4 - len(rooms[final]))
      new_room = tuple(new_room)
      assert(len(new_room) <= 4)

      new_state = (tuple(new_hallway), tuple([rooms[j] if j != final else new_room for j in range(4)]))
      yield (new_state, energy*ENERGY[final])


  # amphipods can go out of their initial room
  for i in range(4):
    if len(rooms[i]) == 0: continue
    a = rooms[i][0]
    (final, has_stopped) = a

    if not has_stopped:
      (mn, mx) = possible_locs_out_of_room(i, hallway)
      for j in range(mn, mx+1):
        if j not in LEGIT_HALLWAY_PLACES: continue
        # TODO: generate new state with top i popped and put in hallway at j

        new_hallway = list(hallway)
        assert(new_hallway[j] is None)
        new_hallway[j] = (final, True)
        energy = abs(j-STACK_PLACES[i])

        new_room = list(rooms[i])
        new_room.pop(0)

        # the energy required
        assert(len(rooms[i]) != 0)
        energy += (5-len(rooms[i]))
        new_room = tuple(new_room)

        new_state = (tuple(new_hallway), tuple([rooms[k] if k != i else new_room for k in range(4)]))
        yield (new_state, energy*ENERGY[final])

def valid_state(state):
  (hallway, rooms) = state
  amphipods = [0 for _ in range(4)]
  for a in hallway:
    if a is None: continue
    (final, has_stopped) = a
    amphipods[final] += 1
  for k in range(4):
    for (final, has_stoped) in rooms[k]:
      amphipods[final] += 1

  return all(amphipods[i] == 4 for i in range(4))

assert(valid_state(initial_state))

g = networkx.DiGraph()

epochs = {0: set([initial_state])}
for epoch in itertools.count(1):
  next_states = set()

  for state in epochs[epoch-1]:
    for (next_state, energy) in children_states(state):
      if not valid_state(next_state):
        pdb.set_trace()

      g.add_edge(state, next_state, energy=energy)
      next_states.add(next_state)

  if len(next_states) == 0: break
  epochs[epoch] = next_states

  print('[+] generated %d new states at epoch %d' % (len(next_states), epoch))


assert(initial_state in g.nodes)

def path_cost(g, path, weight='energy'):
  return sum([g[path[i]][path[i+1]][weight] for i in range(len(path)-1)])

def gen_goals():
  for suitable_rooms in itertools.product((True, False), repeat=16):
    stacks = [[] for i in range(4)]
    suitable_rooms = list(suitable_rooms)
    for i in range(4):
      stacks[i].append((i, suitable_rooms.pop()))
      stacks[i].append((i, suitable_rooms.pop()))
      stacks[i].append((i, suitable_rooms.pop()))
      stacks[i].append((i, suitable_rooms.pop()))
    
    assert(len(suitable_rooms) == 0)
    assert(len(stacks) == 4)
    assert(all(len(stacks[i]) == 4 for i in range(4)))

    for i in range(4):
      stacks[i] = tuple(stacks[i])

    yield ((None, None, None, None, None, None, None, None, None, None, None),
      tuple(stacks))

reachable_goals = []
for goal in gen_goals():
  if goal in g.nodes and networkx.has_path(g, initial_state, goal):
    path = networkx.shortest_path(g, initial_state, goal, weight='energy')
    assert(path)
    reachable_goals.append((goal, path_cost(g, path)))
assert(reachable_goals)

print(min(reachable_goals, key=lambda x: x[1]))
