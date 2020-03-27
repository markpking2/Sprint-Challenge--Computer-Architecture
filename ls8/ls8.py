#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *


if len(sys.argv) != 2:
    print('Missing arguments. Example: python ls8.py file')
    sys.exit(1)

path = sys.argv[1]

cpu = CPU()

cpu.load(path)
cpu.run()
