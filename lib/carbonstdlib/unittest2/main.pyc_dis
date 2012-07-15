#Embedded file name: c:\depot\games\branches\release\EVE-TRANQUILITY\carbon\common\stdlib\unittest2\main.py
import sys
import os
import types
from unittest2 import loader, runner
USAGE_AS_MAIN = "Usage: %(progName)s [options] [tests]\n\nOptions:\n  -h, --help       Show this message\n  -v, --verbose    Verbose output\n  -q, --quiet      Minimal output\n\nExamples:\n  %(progName)s test_module                       - run tests from test_module\n  %(progName)s test_module.TestClass             - run tests from\n                                                   test_module.TestClass\n  %(progName)s test_module.TestClass.test_method - run specified test method\n\n[tests] can be a list of any number of test modules, classes and test\nmethods.\n\nAlternative Usage: %(progName)s discover [options]\n\nOptions:\n  -v, --verbose    Verbose output\n  -s directory     Directory to start discovery ('.' default)\n  -p pattern       Pattern to match test files ('test*.py' default)\n  -t directory     Top level directory of project (default to\n                   start directory)\n\nFor test discovery all test modules must be importable from the top\nlevel directory of the project.\n"
USAGE_FROM_MODULE = "Usage: %(progName)s [options] [test] [...]\n\nOptions:\n  -h, --help       Show this message\n  -v, --verbose    Verbose output\n  -q, --quiet      Minimal output\n\nExamples:\n  %(progName)s                               - run default set of tests\n  %(progName)s MyTestSuite                   - run suite 'MyTestSuite'\n  %(progName)s MyTestCase.testSomething      - run MyTestCase.testSomething\n  %(progName)s MyTestCase                    - run all 'test*' test methods\n                                               in MyTestCase\n"
if __name__ == '__main__':
    USAGE = USAGE_AS_MAIN
else:
    USAGE = USAGE_FROM_MODULE

class TestProgram(object):
    USAGE = USAGE

    def __init__(self, module = '__main__', defaultTest = None, argv = None, testRunner = None, testLoader = loader.defaultTestLoader, exit = True, verbosity = 1):
        if isinstance(module, basestring):
            self.module = __import__(module)
            for part in module.split('.')[1:]:
                self.module = getattr(self.module, part)

        else:
            self.module = module
        if argv is None:
            argv = sys.argv
        self.exit = exit
        self.verbosity = verbosity
        self.defaultTest = defaultTest
        self.testRunner = testRunner
        self.testLoader = testLoader
        self.progName = os.path.basename(argv[0])
        self.parseArgs(argv)
        self.runTests()

    def usageExit(self, msg = None):
        if msg:
            print msg
        print self.USAGE % self.__dict__
        sys.exit(2)

    def parseArgs(self, argv):
        if len(argv) > 1 and argv[1].lower() == 'discover':
            self._do_discovery(argv[2:])
            return
        import getopt
        long_opts = ['help', 'verbose', 'quiet']
        try:
            options, args = getopt.getopt(argv[1:], 'hHvq', long_opts)
            for opt, value in options:
                if opt in ('-h', '-H', '--help'):
                    self.usageExit()
                if opt in ('-q', '--quiet'):
                    self.verbosity = 0
                if opt in ('-v', '--verbose'):
                    self.verbosity = 2

            if len(args) == 0 and self.defaultTest is None:
                self.testNames = None
            elif len(args) > 0:
                self.testNames = args
                if __name__ == '__main__':
                    self.module = None
            else:
                self.testNames = (self.defaultTest,)
            self.createTests()
        except getopt.error as msg:
            self.usageExit(msg)

    def createTests(self):
        if self.testNames is None:
            self.test = self.testLoader.loadTestsFromModule(self.module)
        else:
            self.test = self.testLoader.loadTestsFromNames(self.testNames, self.module)

    def _do_discovery(self, argv, Loader = loader.TestLoader):
        import optparse
        parser = optparse.OptionParser()
        parser.add_option('-v', '--verbose', dest='verbose', default=False, help='Verbose output', action='store_true')
        parser.add_option('-s', '--start-directory', dest='start', default='.', help="Directory to start discovery ('.' default)")
        parser.add_option('-p', '--pattern', dest='pattern', default='test*.py', help="Pattern to match tests ('test*.py' default)")
        parser.add_option('-t', '--top-level-directory', dest='top', default=None, help='Top level directory of project (defaults to start directory)')
        options, args = parser.parse_args(argv)
        if len(args) > 3:
            self.usageExit()
        for name, value in zip(('start', 'pattern', 'top'), args):
            setattr(options, name, value)

        if options.verbose:
            self.verbosity = 2
        start_dir = options.start
        pattern = options.pattern
        top_level_dir = options.top
        loader = Loader()
        self.test = loader.discover(start_dir, pattern, top_level_dir)

    def runTests(self):
        if self.testRunner is None:
            self.testRunner = runner.TextTestRunner
        if isinstance(self.testRunner, (type, types.ClassType)):
            try:
                testRunner = self.testRunner(verbosity=self.verbosity)
            except TypeError:
                testRunner = self.testRunner()

        else:
            testRunner = self.testRunner
        self.result = testRunner.run(self.test)
        if self.exit:
            sys.exit(not self.result.wasSuccessful())


main = TestProgram