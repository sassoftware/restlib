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


import cgi
import logging
import os
import urllib

log = logging.getLogger(__name__)


class Request(object):
    """
    Reqest object.  Describes the request that has been sent in to be
    processed.

    @param req: the underlying request object from the http server.
    @param path: the piece of the path that has already been processed.

    The Request object is mostly a data dictionary that contains the following
    user-accessible pieces.

    path: The entire path - everything to the left of the / after the hostname
    in the url.
    unparsedPath: The path that is still to be processed.
    basePath: the parsed path.
    baseUrl: the basePath with the protocol, port and host prepended.
    host: the host.
    method: the http method that was used - e.g. GET, POST, DELETE, PUT.
    headers: request headers that were sent.
    GET: any query string passed in, stored in a dictionary
    POST: any query string passed in via the request body

    Beyond that, request objects also have the following methods:
    url, read, _getReadFd, getContentLength.

    Url allows you to construct a url that contains the appropriate path
    for this request.  Read allows you to read the body of the request, if it
    has not already been read in as a part of creating the POST field.
    _getReadFd allows you to control the reading directly and getContentLength
    tells you how much data is expected to be uploaded.
    """

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
        """
        Returns a file descriptor for the socket that contains the current
        request.
        """
        raise NotImplementedError()

    def getContentLength(self):
        """
        Returns the expected content length to be read from the current
        request.
        """
        return int(self.headers.get('content-length') or 0)

    def _getPostData(self):
        """
        Internal.  Reads in the body from the current request and converts
        it into a form dictionary, which it returns.  Only applies if the
        content type for the
        request is multipart/form-data or application/x-www-form-urlencoded.
        """
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
        """
        Takes a location as described by the url dict entries in the root
        controller for the request.  Traverse controllers building up the
        url that is required to get there.  If more parameters are presented
        than there are location components, the additional parameters will be
        appended on as sub directories.

        The final position arg may be a tuple instead of a string, in which
        case it will be converted into a querystring.

        @param baseUrl: allows a different initial url to be started with.
        This may be needed if you want to switch from http to https, for
        example.  Keyword only.
        """
        root = self.rootController
        params = list(args)
        baseUrl = kw.pop('baseUrl', None)
        if baseUrl is None:
            baseUrl = self.baseUrl
        if baseUrl.endswith('/'):
            baseUrl = baseUrl[:-1]
        url = [baseUrl]
        if location:
            # traverse controllers, adding in model parameter
            # as needed.
            for part in location.split('.'):
                if root.modelName:
                    url.append(_encode(params[0]))
                    params = params[1:]
                url.append(_encode(part))
                # update what we consider "root" as we traverse the tree.
                root = root.urls[part]

        if params:
            for param in params:
                if isinstance(param, (list, tuple)):
                    # don't create new entry because we don't want an additional
                    # / before the ? on the end.
                    url[-1] += _createQuerystring(param)
                else:
                    url.append(_encode(param))
        elif getattr(root, 'modelName', None):
            # no model or we're getting the index.
            url.append('')
        return '/'.join(url)

def _encode(param):
    """
    Ensures the parameter is url-safe.
    """
    if isinstance(param, unicode):
        return urllib.quote(param.encode('utf8'))
    return urllib.quote(param)

def _createQuerystring(query_tuples):
    """
    Given a list of (k,v) query tuples, will convert them into a query string
    to be used in a url.
    """
    return "?" + ("&".join( "%s=%s" %
                  (k, _encode(v)) for (k, v) in query_tuples))
