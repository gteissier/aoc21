#!/usr/bin/env python3

from binascii import unhexlify
from io import BytesIO
import sys
import functools

'''
when processing bits as numbers, leading zeroes get lost
you have been warned
'''

class EOF(Exception): pass

def hex2bits(hex):
  bits = ''
  for c in hex:
    if c in '0123456789':
      bits += bin(ord(c)-ord('0'))[2:].zfill(4)
      assert(len(bits) % 4) == 0
    elif c in 'ABCDEF':
      bits += bin(ord(c)-ord('A')+0xa)[2:].zfill(4)
      assert(len(bits) % 4) == 0
    else: assert(False)
  return bits

class BitReader:
  def __init__(self, hex=None, bits=None):
    if bits is None:
      assert(hex)
      bits = hex2bits(hex).encode()

    self.f = BytesIO(bits)

  def read(self, n):
    data = self.f.read(n)
    if len(data) != n: raise EOF()
    return data




def read_header(f):
  version = f.read(3)
  typeID = f.read(3) 
  return (int(version, 2), int(typeID, 2))

def read_packet(f, skip_trailer=True):
  (version, typeID) = read_header(f)
  if typeID == 4:
    consumed = 0
    num = b''
    while True:
      not_ending = int(f.read(1), 2)
      limb = f.read(4)
      consumed += 5
      num += limb
      if not_ending == 0: break

    if skip_trailer:
      # trailing padding
      while consumed % 4 != 0:
        b = f.read(1)
        consumed += 1

    return (version, typeID, int(num, 2))

  else:
    lengthTypeID = int(f.read(1), 2)
    if lengthTypeID == 0:
      total_bits = int(f.read(15), 2)

      subcontent = f.read(total_bits)
      assert(len(subcontent) == total_bits)

      subf = BitReader(bits=subcontent)

      subpackets = []
      while True:
        try:
          packet = read_packet(subf, skip_trailer=False)
        except EOF:
          break
        subpackets.append(packet)

      return (version, typeID, subpackets)
    elif lengthTypeID == 1:
      subpackets = []
      number_subpackets = int(f.read(11), 2)
      for i in range(number_subpackets):
        subpackets.append(read_packet(f, skip_trailer=False))

      return (version, typeID, subpackets)

def operate(pkt):
  (version, typeID, val) = pkt

  if typeID == 4: return val
  elif typeID == 0:
    return sum([operate(subpkt) for subpkt in val])
  elif typeID == 1:
    return functools.reduce(lambda x,y: x*y, [operate(subpkt) for subpkt in val], 1)
  elif typeID == 2:
    return min([operate(subpkt) for subpkt in val])
  elif typeID == 3:
    return max([operate(subpkt) for subpkt in val])
  elif typeID == 5:
    pkt0, pkt1 = val[:2]
    if operate(pkt0) > operate(pkt1): return 1
    else: return 0
  elif typeID == 6:
    pkt0, pkt1 = val[:2]
    if operate(pkt0) < operate(pkt1): return 1
    else: return 0
  elif typeID == 7:
    pkt0, pkt1 = val[:2]
    if operate(pkt0) == operate(pkt1): return 1
    else: return 0

  assert(False)

'''
for sample in ['8A004A801A8002F478', '620080001611562C8802118E34', 'C0015000016115A2E0802F182340',
  'A0016C880162017C3686B18A3D4780']:
'''

import sys
if len(sys.argv) == 2:
  sample = sys.argv[1]
else:
  sample = sys.stdin.read().rstrip('\n')

print('=> ', sample)
br = BitReader(hex=sample)
ret = read_packet(br)
print(operate(ret))
