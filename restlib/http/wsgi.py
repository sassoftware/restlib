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
