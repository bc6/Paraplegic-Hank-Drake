import sys
import pdb

def startDebugging():
    pdb.post_mortem(sys.exc_info()[2])


exports = {'debug.startDebugging': startDebugging}

