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
try:
    from mod_python import apache
except ImportError:
    apache = None

from restlib.http import handler, request

class ModPythonRequest(request.Request):

    def read(self, size=-1):
        if size == -1:
            size = self.getContentLength()
        return self._req.read(size)

    def getContentLength(self):
        return int(self.headers.get('content-length', 0))

    def _getHost(self):
        return self._req.headers_in['host'].split(':')[0]

    def _getFullPath(self):
        return self._req.unparsed_uri

    def _getReadFd(self):
        return self._req

    def _getRemote(self):
        "Return the C{(address, port)} of the remote host."
        return self._req.connection.remote_addr

    def _getUri(self):
        return self._req.uri[len(self.basePath):]

    def _getHeaders(self):
        return self._req.headers_in

    def _getHttpMethod(self):
        return self._req.method

    def _getBaseUrl(self):
        secure = (self._req.subprocess_env.get('HTTPS', 'off').lower() == 'on')
        proto = (secure and "https") or "http"
        return "%s://%s%s" % (proto, self._req.headers_in['Host'],
                              self.basePath)

class ModPythonHttpHandler(handler.HttpHandler):
    requestClass = ModPythonRequest

    def handle(self, req, url):
        request = self.requestClass(req, url)
        response = self.getResponse(request)
        length = response.getLength()
        if length is not None:
            response.headers['content-length'] = str(length)
        contentType = response.headers.pop('content-type')
        req.content_type = contentType
        for header, value in response.headers.items():
            req.headers_out[header] = str(value)
        req.status = response.status
        req.send_http_header()
        if response.status in (200, 401):
            if response.getFilePath():
                req.sendfile(response.getFilePath())
            else:
                rawResponse = response.get()
                if type(rawResponse) is str:
                    req.write(rawResponse)
                else:
                    for rawStr in rawResponse:
                        req.write(rawStr)
        else:
            rawResponse = response.get()
            if not rawResponse:
                # Use apache's default status pages.
                return response.status
            req.write(rawResponse)

        return apache.DONE
