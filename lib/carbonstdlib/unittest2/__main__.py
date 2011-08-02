import sys
if sys.argv[0].endswith('__main__.py'):
    sys.argv[0] = 'unittest2'
from unittest2.main import main
main(module=None)

