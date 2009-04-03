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
import cgi
import urllib

class Request(object):

    def __init__(self, req, path):
        self._req = req
        self.path = self._getFullPath()
        # Path only (no query part)
        if path.startswith('/'):
            path = path[1:]
        self.unparsedPath = path

        # Everything before the url we're parsing
        if self.unparsedPath:
            # watch out for empty unparsedPath -- string[:-0] == ''
            self.basePath = self.path[:-len(self.unparsedPath)]
        else:
            self.basePath = self.path
        self.baseUrl = self._getBaseUrl()
        self.host = self._getHost()
        self.headers = self._getHeaders()

        method = self._getHttpMethod()

        # _getGetData also sets self.path if it contains a query string
        self.GET = self._getGetData()
        if method != 'GET':
            self.POST = self._getPostData()
        else:
            self.POST = {}

        # If the method was passed in the URL as ?_method=GET, then override
        # the request's method
        method = self.GET.pop('_method', method)
        method = self.POST.pop('_method', method)
        self.method = method

    def getHostWithProtocol(self):
        return self.baseUrl[:-len(self.basePath)]

    def _getBaseUrl(self, url):
        raise NotImplementedError()

    def _getHttpMethod(self):
        raise NotImplementedError()

    def _getHost(self):
        raise NotImplementedError()

    def _getHeaders(self):
        raise NotImplementedError()

    def _getReadFd(self):
        raise NotImplementedError()

    def _getPostData(self):
        # cgi will read the body when it doesn't recognize the content type
        ctypes = set(['multipart/form-data',
                      'application/x-www-form-urlencoded'])
        contentType = self.headers.get('content-type', None)
        if contentType not in ctypes:
            return {}
        fs =  cgi.FieldStorage(self._getReadFd(), self.headers,
                           environ = {'REQUEST_METHOD' : self._getHttpMethod()})
        d = {}
        for key in fs.keys():
            d[key] = fs.getvalue(key)
        return d

    def _getGetData(self):
        # Side-effect is to set 
        uri, query = urllib.splitquery(self.unparsedPath)
        if query:
            self.unparsedPath = uri
            # Force FieldStorage to parse the query string for us. We need to
            # manufacture a Content-Type that points cgi to the query instead
            # of the body
            # We use an rfc822.Message instead of a dictionary because of the
            # case-insensitive nature of the headers
            headers = cgi.rfc822.Message(cgi.StringIO(
                'Content-Type: application/x-www-form-urlencoded'))
            fs = cgi.FieldStorage(fp = None,
                    headers = headers,
                    environ = { 'REQUEST_METHOD' : 'GET',
                                'QUERY_STRING' : query})
            d = {}
            for key in fs.keys():
                d[key] = fs.getvalue(key)
            return d
        return {}

    def url(self, location, *args, **kw):
        root = self.rootController
        params = list(args)
        baseUrl = self.baseUrl
        if baseUrl.endswith('/'):
            baseUrl = baseUrl[:-1]
        url = [baseUrl]
        if location:
            location = location.split('.')

        def toUtf(x):
            if isinstance(x, unicode):
                return x.encode('utf8')

            return x

        def extend(x):
            if type(x) is list:
                url[-1] += "?"
                url[-1] += ("&".join( "%s=%s" %
                        (k, urllib.quote(toUtf(v))) for (k, v) in x))
            else:
                url.append(urllib.quote(toUtf(x)))

        while location:
            if root.modelName:
                extend(params[0])
                params = params[1:]
            extend(location[0])
            root = root.urls[location[0]]
            location = location[1:]

        if params:
            for param in params:
                extend(param)
        elif getattr(root, 'modelName', None):
            # no model or we're getting the index.
            extend('')
        return '/'.join(url)


