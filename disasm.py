#!/usr/bin/env python3
import urllib.request
import subprocess
import argparse
import json
import sys
import os
import re

def find_abc(swf, names):
    abc = list()
    first = None
    tags = subprocess.check_output(['java', '-jar', 'bin/ffdec/ffdec.jar', '-dumpSWF', swf]).decode()
    for tag, script in re.findall(r'^[0-9a-f]+: +(\d+). DoABC2 \((.+)\)', tags, re.MULTILINE):
        tag = int(tag)
        basename = os.path.basename(script)
        if not first:
            first = tag
        if basename in names:
            abc.append(tag - first)
    return abc

def fetch(swf, test_server=False, swf_file=None):
    print('Retrieving latest manifest')
    if test_server:
        base = 'https://public-deploy2.test-eu.tankionline.com/libs/'
    else:
        base = 'https://s.eu.tankionline.com/libs/'
    with urllib.request.urlopen(base + 'manifest.json') as f:
        data = json.load(f)

    print('Retrieving %s' % swf)
    urllib.request.urlretrieve(base + data[swf], swf_file or swf)

def disasm(swf, abcs, write_includes=True):
    swf_name = os.path.basename(swf).split('.')[0]

    print('Exporting DoABCs')
    subprocess.call(['bin/abcexport', swf])

    print('Disassembling..')
    fnpattern = re.compile(swf_name + r'-(\d+).abc')
    for match in filter(None, (re.match(fnpattern, x) for x in os.listdir('src'))):
        fname = os.path.join('src', match.group(0))
        if int(match.group(1)) in abcs:
            print('..{0}'.format(fname))
            subprocess.call(['bin/rabcdasm', fname])
        os.remove(fname)

    print('Parsing includes')
    includes = dict()
    fnpattern = re.compile(swf_name + r'-(\d+).main.asasm')
    for r, _, f in os.walk('src'):
        for match in filter(None, (re.match(fnpattern, x) for x in f)):
            fname = os.path.join(r, match.group(0))
            with open(fname) as f:
                script = f.read()
            for line in script.splitlines():
                split = line.strip().split(' ')
                if split[0] == '#include':
                    include = split[1].strip('"')
                    includes.setdefault(match.group(1), list()).append(include)
            os.remove(fname)

    if write_includes:
        with open('build.json', 'w') as f:
            json.dump({'file': os.path.basename(swf), 'include': includes}, f, indent=4, sort_keys=True)

def fix_dirs():
    print('Fixing directory structure')
    for r, d, f in os.walk('src', topdown=False):
        parts = r.strip(os.path.sep).split(os.path.sep)
        if len(parts) == 1:
            break
        del parts[1]
        newr = os.path.sep.join(parts)
        os.makedirs(newr, exist_ok=True)
        for file in f:
            os.rename(os.path.join(r, file), os.path.join(newr, file))
        for dir in d:
            os.rmdir(os.path.join(r, dir))
        if len(parts) == 1:
            os.rmdir(r)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch and disassemble Tanki Online binaries.')
    parser.add_argument('swf', help='filename of the swf to process')
    parser.add_argument('scripts', help='scripts to disassemble', nargs='*')
    parser.add_argument('-l', '--local', help='disassemble local binary if present', action='store_true')
    parser.add_argument('-t', '--test', help='fetch files from the test server', action='store_true')
    parser.add_argument('-p', '--patch', help='apply patch file')
    args = parser.parse_args()

    subprocess.check_call(['git', 'checkout', 'master'])
    subprocess.call(['git', 'branch', '-D', 'dev'])
    subprocess.check_call(['git', 'checkout', '-b', 'dev'])

    os.mkdir('src')
    swf = os.path.join('src', args.swf)
    if args.local and os.path.exists(args.swf):
        os.rename(args.swf, swf)
    else:
        fetch(args.swf, args.test, swf)

    patch = args.patch or 'tanki.patch'
    scripts = args.scripts
    if args.patch:
        with open(args.patch, 'r', encoding='utf-8') as f:
            patch_scripts = re.findall(r'\+\+\+ .+\/(.+?)\..+', f.read())
        print('Scripts from patch:')
        print(', '.join(patch_scripts))
        scripts += patch_scripts

    abc = find_abc(swf, args.scripts)
    disasm(swf, abc)
    fix_dirs()
    os.replace(swf, args.swf)
    subprocess.check_call(['git', 'add', 'src'])
    subprocess.check_call(['git', 'commit', '-m', 'disassembly'])
    if os.path.exists(patch):
        subprocess.check_call(['git', 'apply', patch])
