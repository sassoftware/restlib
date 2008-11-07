#
# Copyright (c) 2008 rPath, Inc.
#
# This program is distributed under the terms of the Common Public License,
# version 1.0. A copy of this license should have been distributed with this
# source file in a file called LICENSE. If it is not present, the license
# is always available at http://www.rpath.com/permanent/licenses/CPL-1.0.
#
# This program is distributed in the hope that it will be useful, but
# without any warranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the Common Public License for
# full details.
#
import re

class _Controller(object):

    modelName = None
    processSuburls = False
    urls = None
    modelRegex = '[^/]*'

    def __init__(self, parent, path, subhandlerParams=None):
        self.parent = parent
        if parent:
            self._url = '%s/%s' % (parent._url, path)
            self.root = parent.root
        else:
            self._url = ''
            self.root = self

        if self.modelName:
            self.baseMethods = dict(POST='create',
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

   def url(self, request, paramName=None):
        url = request.baseUrl + self._url
        if paramName:
            url = '%s/%s' % (url, paramName)
        return url

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
            if hasattr(controller, 'getController'):
                return controller.getController(method, url, args, kwargs)
            if hasattr(controller, '__call__'):
                return controller, url, args, kwargs
        raise NotImplementedError


class RestController(_Controller):
    """
    @cvar urls: A dictionary of controllers for the I{head}
    part of the URL. If the controller is a string, the handler's attribute is
    returned; otherwise (assuming it's a class), a controller object is
    instantiated.
    @type urls: C{dict}
    """

    def handle(self, url, request):
        # FIXME: this is not used in live code anymore.
        method = request.method
        controller, remainder, args, kw = self.getController(method, url,
                                                             (), {})
        # NOTE: the above could be cached pretty easily.
        request.unparsedPath = remainder
        return controller(request, *args, **kw)

    def index(self, request, *args, **kwargs):
        raise NotImplementedError

    def process(self, request, *args, **kwargs):
        raise NotImplementedError

    def create(self, request, *args, **kwargs):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        raise NotImplementedError

    def destroy(self, request, *args, **kwargs):
        raise NotImplementedError

    def update(self, request, *args, **kwargs):
        raise NotImplementedError
