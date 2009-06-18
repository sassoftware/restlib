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
import BaseHTTPServer
import os
import socket
import sys

from restlib.http import handler, request

from restlib.response import Response

class SimpleHttpRequest(request.Request):
    def _setProperties(self):
        self.headers = self._req.headers
        self.method = self._req.command
        self.remote = self._req.client_address

    def _getReadFd(self):
        return self._req.rfile

    def _getRawPath(self):
        return self._getHostRootURL(), self._req.path

    def _getHostRootURL(self):
        if 'host' not in self._req.headers:
            host = '%s:%s' % (self._req.server.server_name,
                             self._req.server.server_port)
        else:
            host = self._req.headers['host']
        return 'http://%s' % (host,)

    def read(self, size=-1):
        if size == -1:
            size = self.getContentLength()
        return self._req.rfile.read(size)

    def getContentLength(self):
        return int(self.headers.get('content-length', 0))


class SimpleHttpHandler(handler.HttpHandler):
    requestClass = SimpleHttpRequest

    def handle(self, simple_req, pathPrefix=''):
        request = self.requestClass(simple_req, pathPrefix)
        response = self.getResponse(request)
        simple_req.send_response(response.status, response.message)
        for header, value in response.headers.items():
            simple_req.send_header(header, value)
        length = response.getLength()
        if length is not None:
            simple_req.send_header("content-length", str(length))
        simple_req.end_headers()
        if response.getFilePath():
            BFSIZE = 65536
            fd = os.open(response.getFilePath(), os.O_RDONLY)
            try:
                s = os.read(fd, BFSIZE)
                while s:
                    simple_req.wfile.write(s)
                    s = os.read(fd, BFSIZE)
            finally:
                os.close(fd)
        else:
            rawResponse = response.get()
            if type(rawResponse) is str:
                simple_req.wfile.write(rawResponse)
            else:
                for rawStr in rawResponse:
                    simple_req.wfile.write(rawStr)

        simple_req.wfile.flush()
        simple_req.connection.shutdown(socket.SHUT_WR)

def serve(port, root_controller, callbacks=None):
    _handler = SimpleHttpHandler(root_controller)
    if callbacks:
        for callback in callbacks:
            _handler.addCallback(callback)

    class BaseRESTHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        handler = _handler

        def do(self):
            self.handler.handle(self, self.path)
        do_GET = do_POST = do_PUT = do_DELETE = do

    server = BaseHTTPServer.HTTPServer(('', port), BaseRESTHandler)
    server.serve_forever()

