#!/usr/bin/python
#
# Copyright (c) rPath, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

if __name__ == '__main__':
    sys.exit(testsuite.main())
