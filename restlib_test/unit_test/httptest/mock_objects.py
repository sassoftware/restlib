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


import StringIO

from restlib.http import simplehttp
from restlib.http.handler import HttpHandler

class MockInnerSimpleHttpRequest(object):
    def __init__(self, method, full_url, host=None, headers=None,
            client_address=None, rfile=None):
        self.command = method
        self.full_url = full_url
        self.path = full_url
        if headers is None:
            headers = {}
        self.headers = headers
        if host is None:
            host = 'localhost'
        headers['host'] =  host
        if client_address is None:
            client_address = ('127.0.0.1', '12000')
        self.client_address = client_address
        if rfile is None:
            rfile = StringIO.StringIO()
        self.rfile = rfile
        self.wfile = StringIO.StringIO()

    def _getFullPath(self):
        return self.full_url


class MockClient(object):
    def __init__(self, controller):
        self.controller = controller

    def get_request(self, method, url):
        req = MockInnerSimpleHttpRequest(method, url)
        request = simplehttp.SimpleHttpRequest(req)
        request.rootController = self.controller
        return request

def get_client(controller):
    return MockClient(controller)

def get_request(controller, url, method='GET'):
    return MockClient(controller).get_request(method, url)

def get_handler(controller):
    return HttpHandler(controller)
