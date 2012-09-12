#!/usr/bin/python
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


if __name__ == '__main__':
    sys.exit(testsuite.main())
