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
