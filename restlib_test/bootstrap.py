import os
import sys

testUtilDir = os.environ.get('TESTUTILS_PATH', '../testutils')
if os.path.exists(testUtilDir):
    sys.path.insert(0, testUtilDir)

try:
    import testrunner
except ImportError:
    raise RuntimeError('Could not find testrunner - set TESTUTILS_PATH')
