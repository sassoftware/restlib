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

