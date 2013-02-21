#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
