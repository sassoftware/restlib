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


class Response(object):
    status = 200
    responses = BaseHTTPServer.BaseHTTPRequestHandler.responses

    def __init__(self, content='', content_type='text/html', status=None,
                 message=None, headers=None):
        self.response = [content]
        if headers is None:
            headers = {}
        self.headers = headers
        self.headers['content-type'] = content_type
        if status:
            self.status = status
        if message is None:
            message = self.responses[self.status][0]
        self.message = message

    def get(self):
        return ''.join(self.response)
    content = property(get)

    def getLength(self):
        # __len__ is a bad idea as it affect __nonzero__
        return sum([len(x) for x in self.response])

    def write(self, txt):
        if not isinstance(txt, str):
            import epdb
            epdb.st()
        self.response.append(txt)

    def redirect(self, url, permanent=False):
        self.headers['location'] = url
        if permanent:
            self.status = 301
        else:
            self.status = 302

class RedirectResponse(Response):
    def __init__(self, url, permanent=False):
        Response.__init__(self)
        self.redirect(url, permanent=permanent)
