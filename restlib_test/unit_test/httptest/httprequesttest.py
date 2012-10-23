#
# Copyright (c) rPath, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


import testsuite

from testrunner import testcase
from testutils import mock

import BaseHTTPServer
import StringIO

from restlib.http import simplehttp, modpython


class RequestTest(testcase.TestCase):
    _pathPrefix = '/TOP'
    _auth = ('user', 'pass')

    def _testRequest1(self, req, expectedPath, expectedMethod):
        self.failUnlessEqual(req.unparsedPath, expectedPath)
        self.failUnlessEqual(req.method, expectedMethod)
        self.failUnlessEqual(sorted(req.headers.items()),
            [ ('content-length', '3'),
                ('content-type', 'text/gibberish'),
                ('host', 'hostname'), ])

    def _getPath(self, path):
        assert path.startswith(self._pathPrefix)
        return path[len(self._pathPrefix):].lstrip('/')

    def testSimpleRequest(self):
        data = "abc"
        path = '/TOP/bar/baz'
        method = 'GET'
        f = StringIO.StringIO(tmpl1 % (method, path, len(data), data))
        _req = SimpleReqHandler(f)
        ret = _req.readFromFile()
        self.failUnlessEqual(ret, True)
        req = simplehttp.SimpleHttpRequest(_req, self._pathPrefix)
        self._testRequest1(req, self._getPath(path), 'GET')

        pathP = path + '?_method=GET'
        f = StringIO.StringIO(tmpl1 % ('POST', pathP, len(data), data))

        _req = SimpleReqHandler(f)
        ret = _req.readFromFile()
        self.failUnlessEqual(ret, True)
        req = simplehttp.SimpleHttpRequest(_req, self._pathPrefix)
        self._testRequest1(req, self._getPath(path), 'GET')

    def testModPythonRequest(self):
        data = "abc"
        path = '/TOP/bar/baz'
        method = 'GET'
        f = StringIO.StringIO(tmpl1 % (method, path, len(data), data))
        _req = FakeModPythonReq(f)
        req = modpython.ModPythonRequest(_req, self._pathPrefix)
        self._testRequest1(req, self._getPath(path), 'GET')

        pathP = path + '?_method=GET'
        f = StringIO.StringIO(tmpl1 % ('POST', pathP, len(data), data))
        _req = FakeModPythonReq(f)
        req = modpython.ModPythonRequest(_req, self._pathPrefix)
        self._testRequest1(req, self._getPath(path), 'GET')


class SimpleReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, dataFile):
        self.rfile = dataFile
        self.wfile = StringIO.StringIO()
        self.client_address = ('0.0.0.0', 65534)

    def readFromFile(self):
        self.raw_requestline = self.rfile.readline()
        if not self.raw_requestline:
            self.close_connection = 1
            return False
        if not self.parse_request(): # An error code has been sent, just exit
            return False
        return True

tmpl1 = """\
%s %s HTTP/1.0
Host: hostname
Content-Type: text/gibberish
Content-Length: %s

%s
"""

class FakeModPythonReq(object):
    def __init__(self, dataFile):
        req = SimpleReqHandler(dataFile)
        ret = req.readFromFile()
        if not ret:
            raise Exception
        self._rfile = req.rfile
        self.headers_in = req.headers
        self.method = req.command
        self.uri = req.path
        self.unparsed_uri = req.path
        self.subprocess_env = {}
        self.connection = mock.MockObject()
        self.connection.remote_addr = ('::', 65534)

    def read(self, *args, **kwargs):
        return self._rfile.read(*args, **kwargs)
