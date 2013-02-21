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
