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


import BaseHTTPServer
import os


class Response(object):
    """
    Response class contains the Response to be sent back from
    a request.
    @param content: content to be returned.  Can be string or list (but not
    other iterables, as we need to be able to get the len() of the response).
    @param content_type: mime type of content.
    @param status: standard integer status code.  Default is 200
    @param message: standard http message to be sent with status code.
    @param headers: dictionary of extra headers to send with response.
    """
    status = 200
    # python has already done the work of converting from status id to
    # short response message for us.
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
            # defaults to class variable
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
        # NOTE: this removes the advantage of having an iterable
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
        self.headers['location'] = url
        self.status = 201
        self.redirect(url)


class PermanentRedirectResponse(RedirectResponse):
    status = 301


class SeeOtherResponse(RedirectResponse):
    status = 303


class CreatedResponse(RedirectResponse):
    status = 201


class FileResponse(Response):
    """
    Returns a response directly from a file directly.  Other paramters
    same as those in a standard response
    @param path: path to the file on disk.
    """

    def getLength(self):
        # mod_python.sendfile sends everything, this makes us work the same on
        # simplehttp server
        return os.stat(self.path).st_size

    def __init__(self, path, content_type='application/octet-stream',
                 status=None, message=None, headers=None):
        Response.__init__(self, content_type=content_type, status=status,
                          message=message, headers=headers)
        self.path = path
