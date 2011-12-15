#
# Copyright (c) 2011 rPath, Inc.
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

import webob
from restlib.http import handler, request


class WebObRequest(request.Request):

    def _setProperties(self):
        self.headers = self._req.headers
        self.method = self._req.method
        self.remote = self._req.remote_addr

    def read(self, size=-1):
        if size == -1:
            size = self.getContentLength()
        return self._req.read(size)

    def _getRawPath(self):
        base = self._req.host_url
        subpath = self._req.url[len(base):]
        return base, subpath

    def _getPostData(self):
        return self._req.POST


class WSGIHandler(handler.HttpHandler):
    requestClass = WebObRequest

    _requestFactory = webob.Request
    _responseFactory = webob.Response

    def __call__(self, environ, start_response):
        request = self._requestFactory(environ)
        response = self.handle(request)
        return response(environ, start_response)

    def handle(self, webreq, pathPrefix=''):
        request = self.requestClass(webreq, pathPrefix)
        response = self.getResponse(request)

        webresp = self._responseFactory()
        webresp.status = response.status
        for header, value in response.headers.items():
            webresp.headers[header] = value
        if response.getFilePath():
            webresp.content_length = response.getLength()
            webresp.body_file = open(response.getFilePath(), 'rb')
        else:
            rawResponse = response.get()
            if response.status != 200 and not rawResponse:
                rawResponse = '<h1>%s</h1>' % webresp.status

            if not isinstance(rawResponse, basestring):
                rawResponse = ''.join(rawResponse)
                webresp.body = rawResponse
            else:
                webresp.body = ''.join(rawResponse)
        return webresp
