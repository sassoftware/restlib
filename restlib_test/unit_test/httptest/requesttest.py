#!/usr/bin/python
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


if __name__ == '__main__':
    sys.exit(testsuite.main())
