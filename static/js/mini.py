#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import os
from os.path import getmtime
import sys
import subprocess


def needs_updating(name):
    name_min = name.replace('.js', '.min.js')
    if not os.path.isfile(name_min):
        return True
    return getmtime(name) > getmtime(name_min)


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 1:
        files = argv[1:]
    else:
        files = [f for f in os.listdir('.')
            if f.endswith('.js') and not f.endswith('.min.js')]
        files = filter(needs_updating, files)
    
    for name in files:
        print 'Minificando', name
        subprocess.call(['java', '-jar', 'compiler.jar', '--js', name,
            '--js_output_file', name.replace('.js', '.min.js')])
    if not files:
        print 'Todo actualizado'

    print 'Concatenando JS centrales > core.min.js'
    subprocess.call('rm core.min.js', shell=True)
    cmd = 'cat json2.min.js polyfills.min.js gmaps.min.js  main.min.js > core.min.js'
    subprocess.call(cmd, shell=True)

