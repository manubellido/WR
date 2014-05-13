#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
import os
from os.path import isfile, getmtime, abspath, dirname, join, normpath
import subprocess


THIS_DIR = abspath(dirname(__file__))
ROOT_DIR = normpath(join(THIS_DIR, '..', '..', 'static', 'js'))
COMPILER = join(THIS_DIR, 'compiler.jar')


def needs_updating(name):
    """Check if a minified file needs updating.
    """
    print 'Verificando actualidad de', name
    name = join(ROOT_DIR, name)
    name_min = name.replace('.js', '.min.js')
    if not isfile(name_min):
        return True
    return getmtime(name) > getmtime(name_min)


if __name__ == "__main__":
    import sys
    
    argv = sys.argv
    if len(argv) > 1:
        files = argv[1:]
    else:
        files = [f for f in os.listdir(ROOT_DIR)
            if f.endswith('.js') and not f.endswith('.min.js')]
        files = filter(needs_updating, files)
    
    for name in files:
        print 'Minificando', name
        filename = join(ROOT_DIR, name)
        subprocess.call(['java', '-jar', COMPILER, '--js', filename,
            '--js_output_file', filename.replace('.js', '.min.js')])
    if not files:
        print 'Todo actualizado'

    print 'Concatenando JS centrales > core.min.js'
    subprocess.call('rm ' + join(ROOT_DIR, 'core.min.js'), shell=True)
    cmd = ' '.join(['cat',
        join(ROOT_DIR, 'json2.min.js'),
        join(ROOT_DIR, 'polyfills.min.js'), 
        join(ROOT_DIR, 'gmaps.min.js'), 
        join(ROOT_DIR, 'main.min.js'),
        '>',
        join(ROOT_DIR, 'core.min.js'),
    ])
    subprocess.call(cmd, shell=True)

