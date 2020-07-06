#!/usr/bin/env python3
import subprocess
import sys

if len(sys.argv) == 2:
    patch = sys.argv[1]
else:
    patch = 'tanki.patch'

with open(patch, 'wb') as f:
    subprocess.check_call(['git', 'diff'], stdout=f)
