#
# Copyright (c) 2008-2009 rPath, Inc.
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
import logging
import os
import urllib

log = logging.getLogger(__name__)


class Request(object):
    # The root controller currently serving this request. This is set
    # externally by the handler.
    rootController = None

    # The URL prefix at which the controller appears to be rooted.
    baseUrl = None

    # The path without any prefix or query arguments.
    path = None

    # Same as above, but elements are removed from the left after a controller
    # is assigned to the request. In other words, this is the unstructured
    # remainder of the path.
    unparsedPath = None

    # The full, (approximately) original URL of this request.
    thisUrl = None

    # Other interesting attributes
    headers = None
    method = None
    remote = None

    # Query arguments
    GET = POST = None

    def __init__(self, req, pathPrefix=''):
        self._req = req

        rawBase, rawPath = self._getRawPath()

        # Normalize and de-prefix the path
        path = rawPath
        if path.startswith(pathPrefix):
            path = path[len(pathPrefix):]
        else:
            log.warning("Path %r does not start with specified prefix %r",
                    path, pathPrefix)
        if path.startswith('/'):
            path = path[1:]

        # Parse and remove query arguments.
        self.path, self.GET = self._splitQuery(path)
        self.unparsedPath = self.path

        self.baseUrl = rawBase + pathPrefix
        self.thisUrl = rawBase + rawPath

        # Fill out the rest of the attributes (headers, method, remote, etc.)
        self._setProperties()

        if self.getContentLength():
            self.POST = self._getPostData()
        else:
            self.POST = {}

        # If the method was passed in the URL as ?_method=GET, then override
        # the request's method
        if '_method' in self.GET:
            self.method = self.GET.pop('_method')

        #log.info("Request:\n" + "\n".join("  %s: %r" % x for x in self.__dict__.items()))

    def _setProperties(self):
        "Fill out extra attributes from the request."
        raise NotImplementedError()

    def _getRawPath(self):
        "Return the current URL of the request, split into host and path."
        raise NotImplementedError()

    def _getReadFd(self):
        raise NotImplementedError()

    def getContentLength(self):
        raise NotImplementedError()

    def _getPostData(self):
        # cgi will read the body when it doesn't recognize the content type
        ctypes = set(['multipart/form-data',
                      'application/x-www-form-urlencoded'])
        contentType = self.headers.get('content-type', None)
        if contentType not in ctypes:
            return {}
        fs =  cgi.FieldStorage(self._getReadFd(), self.headers,
                           environ = {'REQUEST_METHOD' : self.method})
        d = {}
        for key in fs.keys():
            d[key] = fs.getvalue(key)
        return d

    @staticmethod
    def _splitQuery(path):
        """
        Split off any query arguments (GET) from C{path}. Returns the path sans
        query, and a dictionary of the parsed arguments.
        """
        path, query = urllib.splitquery(path)
        args = {}
        if query:
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
            for key in fs.keys():
                args[key] = fs.getvalue(key)
        return path, args

    def url(self, location, *args, **kw):
        root = self.rootController
        params = list(args)
        baseUrl = kw.pop('baseUrl', None)
        if baseUrl is None:
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
