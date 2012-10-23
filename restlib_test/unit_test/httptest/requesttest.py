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


class RequestTest(testcase.TestCase):
    def testUrl(self):
        req = mock_objects.get_request(book_site.SiteController(), '/')
        url = req.url('books.chapters.search', 'foo', '1')
        self.assertEqual('http://localhost/books/foo/chapters/1/search', url)
        url = req.url('books.chapters.search', 'foo', '1', baseUrl='https://localhost')
        self.assertEqual('https://localhost/books/foo/chapters/1/search', url)
        url = req.url('books.chapters.search', 'foo', '1', [('foo', 'bar'),
                                                            ('bam', 'baz')])
        self.assertEqual('http://localhost/books/foo/chapters/1/search?foo=bar&bam=baz', url)

    def testGetData(self):
        req = mock_objects.get_request(book_site.SiteController(), '/?param=blah;param=blah2;param2=foo')
        self.failUnlessEqual(req.GET['param'], ['blah', 'blah2'])
        self.failUnlessEqual(req.GET['param2'], 'foo')
