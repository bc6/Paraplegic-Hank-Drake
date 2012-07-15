#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\lib\jinja2\_markupsafe\_bundle.py
import sys
import os
import re

def rewrite_imports(lines):
    for idx, line in enumerate(lines):
        new_line = re.sub('(import|from)\\s+markupsafe\\b', '\\1 jinja2._markupsafe', line)
        if new_line != line:
            lines[idx] = new_line


def main():
    if len(sys.argv) != 2:
        print 'error: only argument is path to markupsafe'
        sys.exit(1)
    basedir = os.path.dirname(__file__)
    markupdir = sys.argv[1]
    for filename in os.listdir(markupdir):
        if filename.endswith('.py'):
            f = open(os.path.join(markupdir, filename))
            try:
                lines = list(f)
            finally:
                f.close()

            rewrite_imports(lines)
            f = open(os.path.join(basedir, filename), 'w')
            try:
                for line in lines:
                    f.write(line)

            finally:
                f.close()


if __name__ == '__main__':
    main()