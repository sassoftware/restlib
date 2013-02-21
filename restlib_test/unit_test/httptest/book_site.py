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
