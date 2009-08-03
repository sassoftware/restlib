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
