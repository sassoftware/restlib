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
