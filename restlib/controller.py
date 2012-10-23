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


import re
import urllib

class _Controller(object):

    # Declarative configuration variables.  The following variables control
    # the behavior of the controller.  See documentation of Controller
    # subclass for what they do.
    modelName = None
    modelRegex = '[^/]*'
    processSuburls = False
    urls = None

    def __init__(self, parent, path, subhandlerParams=None):
        """

        """
        self.parent = parent
        if parent:
            self._url = '%s/%s' % (parent._url, path)
            self.root = parent.root
        else:
            self._url = ''
            self.root = self

        if self.modelName:
            self.baseMethods = dict(POST='create',
                                    DELETE='destroy_all',
                                    PUT='update_all',
                                    GET='index')
            self.modelMethods = dict(POST='process',
                                GET='get',
                                PUT='update',
                                DELETE='destroy')
        else:
            self.baseMethods = dict(POST='process',
                                    GET='index',
                                    PUT='update',
                                    DELETE='destroy')


        if not subhandlerParams:
            subhandlerParams = []
        self.urls = self._initializeUrls(self.urls, subhandlerParams)

    def _initializeUrls(self, urls, subhandlerParams):
        if not urls:
            return {}
        newUrls = {}
        for key, handler in urls.items():
            if isinstance(handler, str):
                newUrls[key] = getattr(self, handler)
            elif isinstance(handler, dict):
                d = {}
                for method, handlerStr in handler.iteritems():
                    d[method] = getattr(self, handlerStr)
                newUrls[key] = d
            else:
                newUrls[key] = handler(self, key, *subhandlerParams)
        return newUrls

    def url(self, request, location, *args):
        return request.url(location, *args)

    def splitId(self, url):
        match = re.match('/?(%s)/?(.*|)' % self.modelRegex, url)
        if match:
            return match.groups()
        raise NotImplementedError

    def splitSubdir(self, url):
        if url[0] == '/':
            url = url[1:]
        parts = url.split('/', 1)
        return (parts + [''])[0:2]

    def getView(self, method, url):
        # FIXME: this should separate into one part that dispatches
        # to the right depth (getController)
        # and a second part that assumes that the current controller 
        # is the right one (getView body)
        url = urllib.unquote(url)
        return self.getController(method, url, (), {})

    def getController(self, method, url, args, kwargs):
        if not url or url == '/':
            viewFnName = self.baseMethods.get(method, None)
            if viewFnName:
                viewFnName = getattr(self, viewFnName)
                return viewFnName, '', args, kwargs
            else:
                raise NotImplementedError
        elif self.modelName:
            modelId, newUrl = self.splitId(url)
            kwargs[self.modelName] = modelId
            return self.getControllerWithId(method, newUrl, args, kwargs)
        else:
            subDir, newUrl = self.splitSubdir(url)
            return self.getNextController(method, subDir, newUrl, args, kwargs)

    def getControllerWithId(self, method, url, args, kwargs):
        controller = None
        if url:
            subDir, newUrl  = self.splitSubdir(url)
            if self.urls and subDir in self.urls:
                controller = self.urls[subDir]
                if isinstance(controller, dict):
                    if method in controller:
                        controller = controller[method]
                    else:
                        raise NotImplementedError
                if hasattr(controller, 'getController'):
                    return controller.getController(method, newUrl,
                                                    args, kwargs)
                return controller, newUrl, args, kwargs
        if not url or self.processSuburls:
            controller = self.modelMethods.get(method, None)
            if controller:
                controller = getattr(self, controller)
                return controller, url, args, kwargs
        raise NotImplementedError

    def getNextController(self, method, subDir, url, args, kwargs):
        if self.urls and subDir in self.urls:
            controller = self.urls[subDir]
            if isinstance(controller, dict):
                if method in controller:
                    controller = controller[method]
            if hasattr(controller, 'getController'):
                return controller.getController(method, url, args, kwargs)
            if hasattr(controller, '__call__'):
                return controller, url, args, kwargs
        raise NotImplementedError


class RestController(_Controller):
    """
    Controller object.  Contains logic for determining
    what view to render.  Also often contains the views that are called
    as methods of this class.

    Any url parsing is controlled by the urls dictionary (described below)
    If there is no url to parse, the following methods are called for each
    HTTP method.  The default implementations raise NotImplementedError,
    which is automatically translated to a 404 response.

    GET: index
    POST: process
    PUT: update
    DELETE: destroy

    These methods will be called with a request object as the first parameter.
    The remainder parameters will be controlled by the process of parsing
    the url structures, but in general will be keywords determined by the
    model controllers that parsed parts of the url structure to get to the
    current controller (see the modelName description for more details).

    The behavior is controlled by several class variables.

    @cvar urls: A dictionary that describes how the controller should
    process the leftmost part of the url.  The keys of the dictionary are
    strings that map to the leftmost part of the url (by default, the part
    between the leftmost slashes).

    * If the value is not a string or a dictionary, it should be a subclass
    of the Controller class (or something that acts like a controller class).

    Example:

    If your top level controller contains:

    {'books'  : BooksController,
     'movies' : MoviesController}

    Then any request to /books will be passed to the BooksController and
    any request to /movies will be passed to the MoviesController.

    * If the value is a string, the string should correspond to a method of the
    current class.  This method will be returned as the view if and only if
    the current controller has parsed the remainder of the url.

    Example:

    If your urls for your top level controller contains:

    { 'people' : 'list_people'}

    And your controller class contains a method:

    def list_people(request):
        return Response('People in this database: john, mary, sue')

    Then the list_people view will be used for the request /people/, but
    not for /people/some/url or /people/

    * If the value is a dictionary, the keys of this subdictionary should be
    http methods (GET, POST, PUT, DELETE), and the values should be either
    strings or subclasses of the controller class as above.

    Example:

    With the following urls dictionary:

    urls = {'invitation'  : { 'POST' : 'send_invitation',
                              'GET'  : 'get_invitation'}}

    A GET request to '/invitation/' will use the 'get_invitation' method,
    a POST request will use the 'send_invitation' method, and a DELETE request
    will return a 404 RequestNotFound error code.

    @cvar modelName: contains the name of the model that this controller
    parses for.  Changes the parsing and dispatching behavior of the controller.
    Also results in the url section parsed as the model being passed into the
    view as a keyword.  The keyword name is the value stored in modelName,
    and the keyword value is the string parsed from the url.

    When creating REST APIs, part of the url often represents
    a particular instance of an object.  For example, /people/john may be
    used to represent a particular person, John.

    To enable this behavior for a particular Controller, set the modelName
    variable to something that can be used as a keyword name in python.

    If there is no url to process, then the following views will be used:

    GET: index
    POST: create
    DELETE: destroy_all
    PUT: update_all

    If there is a url to process, then the first part of the url will be used
    as the model parameter (and passed in as a keyword to whatever view is
    finally called).  By default, the model parameter will be assumed to be
    whatever is between the first two slashes, but that behavior can be
    controlled by the splitId() method.

    If after splitting out the model parameter, there is more url to parse,
    then the urls dictionary will be used to determine how to process the rest
    of the url.  Otherwise, the following views will be used:

    GET: get
    PUT: update
    POST: process
    DELETE: destroy

    Example:


    class BookController(Controller):
        modelName = 'bookName'
        urls = {'chapter' : ChapterController}

        def get(self, request, bookName):
            # get book with name bookName and return some representation of it
            # return Response

        def index(self, request):
            # list all books and return some representation
            # return Response

        def destroy(self, request, bookName):
            # get and delete bookName
            # return "Deleted" response or redirect to index.

    class RootController(Controller):
        urls = {'books' : BookController }

    The following urls would call the following methods:

    GET /books/ - BookController.index
    GET /books/Snow+Crash - BookController.get with bookName="Snow Crash"
    DELETE /books/Snow+Crash - BookController.destroy with bookName="Snow Crash"
    DELETE /books - 404 because destroy_all is not implemented

    @cvar modelRegex: Controls the way model ids are parsed out of urls.
    Defaults to '[^/]*' which treats anything between two /'s as the model
    name, (the empty string will be used if two /s are right next to each
    other.)  If you wish to fully control the model parsing, you can override
    the splitId method.

    @cvar processSuburls: defaults to False.  If set to True, any extra
    remaining url (after processing the modelName if any) will be ignored and 
    instead stored in request.unparsedPath.  The view to be returned will be
    processed as if there were no url remaining to be parsed.
    """

    ## Base methods
    # POST
    def create(self, request, *args, **kwargs):
        raise NotImplementedError
    # GET (also non-model)
    def index(self, request, *args, **kwargs):
        raise NotImplementedError
    # PUT
    def update_all(self, request, *args, **kwargs):
        raise NotImplementedError
    # DELETE
    def destroy_all(self, request, *args, **kwargs):
        raise NotImplementedError

    ## Model & non-model methods
    # POST
    def process(self, request, *args, **kwargs):
        raise NotImplementedError
    # GET (model only)
    def get(self, request, *args, **kwargs):
        raise NotImplementedError
    # PUT
    def update(self, request, *args, **kwargs):
        raise NotImplementedError
    # DELETE
    def destroy(self, request, *args, **kwargs):
        raise NotImplementedError
