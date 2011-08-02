import sys
import os

def find_package(dir):
    dir = os.path.abspath(dir)
    orig_dir = dir
    path = map(os.path.abspath, sys.path)
    packages = []
    last_dir = None
    while 1:
        if dir in path:
            return '.'.join(packages)
        packages.insert(0, os.path.basename(dir))
        dir = os.path.dirname(dir)
        if last_dir == dir:
            raise ValueError('%s is not under any path found in sys.path' % orig_dir)
        last_dir = dir




