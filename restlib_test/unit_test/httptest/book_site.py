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


from restlib.controller import RestController

from restlib import response

class Book(object):
    def __init__(self, name):
        self.name = name
        self.chapters = [ (str(x), 'chapter text %s' % x) for x in range(5) ]

class BaseController(RestController):

    def __init__(self, parent, path, books):
        self.booklist = books
        RestController.__init__(self, parent, path, [books])


class ChapterController(BaseController):
    modelName = 'chapterName'
    
    urls = {'search' : {'GET' : 'search'}}

    def search(self):
        pass

class BookController(BaseController):
    modelName = 'bookName'
    urls = {'chapters' : ChapterController }

    def get(self, request, bookName):
        return response.Response(bookName)

class SiteController(RestController):
    urls = {'books' : BookController }
    def __init__(self):
        self.books = {'foo' : Book('foo'), 'bar' : Book('bar')}
        RestController.__init__(self, None, None, [self.books])
