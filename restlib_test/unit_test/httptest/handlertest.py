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

import BaseHTTPServer
import StringIO

from restlib.http import request
from restlib import controller

import mock_objects
import book_site


class CallbackRecorder(object):
    callbacks = []
    def __init__(self, id):
        self.id = id

    def processRequest(self, request):
        self.callbacks.append('request %s' % self.id)

    def processMethod(self, request, fn, args, kw):
        self.callbacks.append('method %s' % self.id)

    def processResponse(self, request, response):
        self.callbacks.append('response %s' % self.id)

    def processException(self, request, class_, err, tb):
        self.callbacks.append('exception %s' % self.id)

class HandlerTest(testcase.TestCase):
    def testHandler(self):
        controller = book_site.SiteController()
        handler = mock_objects.get_handler(controller)
        request = mock_objects.get_request(controller, '/books/foo')
        handler.addCallback(CallbackRecorder(1))
        handler.addCallback(CallbackRecorder(2))
        response = handler.getResponse(request)
        self.failUnlessEqual(response.get(), 'foo')
        self.assertEquals(CallbackRecorder.callbacks, ['request 1', 'request 2',
                                                       'method 1', 'method 2',
                                                       'response 2', 'response 1'])
