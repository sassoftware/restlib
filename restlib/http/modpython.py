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


try:
    from mod_python import apache
except ImportError:
    apache = None

from restlib.http import handler, request

class ModPythonRequest(request.Request):

    # implementation details for converting from a mod_python request
    # object into a standard restlib Request.

    def _setProperties(self):
        self.headers = self._req.headers_in
        self.method = self._req.method
        self.remote = self._req.connection.remote_addr

    def read(self, size=-1):
        if size == -1:
            size = self.getContentLength()
        return self._req.read(size)

    def _getRawPath(self):
        """
        Returns the entire, raw request URI, split into two parts. The first
        part is the schema, host, and port, and the second part is the path.
        """
        uri = self._req.unparsed_uri

        if '://' in uri:
            # e.g. http://somehost/foo/bar?baz
            # Appears in some cases involving proxies.
            if uri.count('/') < 3:
                # http://somehost
                uri += '/'
            uri = '/' + uri.split('/', 3)[3]
        else:
            # e.g. /foo/bar?baz
            # This is the normal case.
            if not uri.startswith('/'):
                uri = '/' + uri

        return self._getHostRootURL(), uri

    def _getReadFd(self):
        return self._req

    def _getHostRootURL(self):
        "Internal function to construct the host URL prefix."
        secure = (self._req.subprocess_env.get('HTTPS', 'off').lower() == 'on')
        proto = (secure and "https") or "http"
        return "%s://%s" % (proto, self._req.headers_in['Host'])


class ModPythonHttpHandler(handler.HttpHandler):
    requestClass = ModPythonRequest

    def handle(self, req, pathPrefix=''):
        """
        Entry point for using restlib with mod_python requests.
        Call this with a mod_python request and a base_url (those parts of the
        url that have already been parsed).

        @param req: mod_python request object
        @param url: base url that has already been parsed.  This part will
        be ignored by restlib.
        """
        # convert from mod_python request to restlib request
        request = self.requestClass(req, pathPrefix)

        # do all actual processing of request.
        response = self.getResponse(request)

        # send restlib response back to mod_python
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
                # TODO: support iterating over content if content is iterable
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
