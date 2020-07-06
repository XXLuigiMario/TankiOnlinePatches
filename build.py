#!/usr/bin/env python3
import subprocess
import shutil
import json
import os

with open('build.json', 'r') as f:
    build = json.load(f)

original = build['file']
patchedfn = original.split('.')[0] + '_patched.swf'
shutil.copyfile(original, patchedfn)

for entry, scripts in build['include'].items():
    file = 'src/include-{0}.asasm'.format(entry)
    print('Processing DoABC #{0}..'.format(entry))
    print('..Generating includes')
    with open(file, 'w') as f:
        f.write('#version 4\n')
        f.write('program\n')
        f.write(' minorversion 16\n')
        f.write(' majorversion 46\n')
        for include in scripts:
            f.write(' #include "{0}"\n'.format(include))
        f.write('end ; program\n')

    print('..Compiling')
    subprocess.call(['bin/rabcasm', file])
    os.remove(file)

    print('..Patching')
    file = file[:-5] + 'abc'
    subprocess.call(['bin/abcreplace', patchedfn, entry, file])
    os.remove(file)

print('Patched changes in {0}'.format(patchedfn))
