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


class Response(object):
    status = 200
    responses = BaseHTTPServer.BaseHTTPRequestHandler.responses

    def __init__(self, content='', content_type='text/html', status=None,
                 message=None, headers=None):
        if isinstance(content, str):
            content = [content]
        self.response = content
        if headers is None:
            headers = {}
        self.headers = headers
        self.headers['content-type'] = content_type
        if status:
            self.status = status
        if message is None:
            message = self.responses[self.status][0]
        self.message = message
        self.path = None

    def get(self):
        return ''.join(self.response)
    content = property(get)

    def getLength(self):
        # __len__ is a bad idea as it affect __nonzero__
        return sum([len(x) for x in self.response])

    def write(self, txt):
        self.response.append(txt)

    def redirect(self, url, status=None):
        self.headers['location'] = url
        if status:
            self.status = status

    def getFilePath(self):
        return self.path


class RedirectResponse(Response):
    status = 302

    def __init__(self, url):
        Response.__init__(self)
        self.redirect(url)


class PermanentRedirectResponse(RedirectResponse):
    status = 301


class SeeOtherResponse(RedirectResponse):
    status = 303


class CreatedResponse(RedirectResponse):
    status = 201


class FileResponse(Response):

    def getLength(self):
        # sendfile sends everything, this makes us work the same on
        # simplehttp server
        return os.stat(self.path).st_size

    def __init__(self, path=None, content_type='application/octet-stream',
                 status=None, message=None, headers=None):
        Response.__init__(self, content_type=content_type, status=status,
                          message=message, headers=headers)
        self.path = path
