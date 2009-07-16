#!/usr/bin/python
import sys,os

sys.path.append('..')
from common.monotesting import *

# sub directories
# Add child test suites to test suite

from all.alltests import *

if os.path.exists('C:'):
    print "Importing Win32 tests"
    from win32.alltests import *
elif os.uname()[0].lower() == 'linux':
    print "Importing Linux tests"
    from linux.alltests import *
elif os.uname()[0].lower() == 'darwin':
    print "Importing Mac OSX tests"
    from macox.alltests import *


if __name__ == '__main__':
    monotesting_main()


# vim:ts=4:expandtab:
