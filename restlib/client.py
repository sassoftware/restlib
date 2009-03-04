#
# Copyright (c) 2008-2009 rPath, Inc.
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

import base64
import httplib
import urllib

class ResponseError(Exception):
    def __init__(self, status, reason, headers, response):
        Exception.__init__(self)
        self.status = status
        self.reason = reason
        self.headers = headers
        self.response = response
        self.contents = response.read()

    def __str__(self):
        return '%s: %s\n%s' % (self.status, self.reason, self.contents)

class Client(object):
    HTTPConnection = httplib.HTTPConnection
    HTTPSConnection = httplib.HTTPSConnection

    def __init__(self, url, headers = None):
        self.scheme = None
        self.user = None
        self.passwd = None
        self.host = None
        self.port = None
        self.path = None
        self.headers = headers or {}

        urltype, url = urllib.splittype(url)
        if urltype:
            self.scheme = urltype.lower()

        host, self.path = urllib.splithost(url)
        if host:
            user_passwd, host = urllib.splituser(host)
            self.host, self.port = urllib.splitport(host)
            if self.port is not None:
                self.port = int(self.port)
            if user_passwd:
                self.user, self.passwd = urllib.splitpasswd(user_passwd)

        if self.scheme not in ['http', 'https']:
            raise ValueError(self.scheme)

        self._connection = None

    def setUserPassword(self, username, password):
        self.user = username
        self.passwd = password

    def connect(self):
        if self.scheme == 'http':
            cls = self.HTTPConnection
        else:
            cls = self.HTTPSConnection
        self._connection = cls(self.host, port = self.port)
        self._connection.connect()
        return self

    def request(self, method, body=None, headers=None):
        hdrs = self.headers.copy()
        hdrs.update(headers or {})
        if self.user is not None and self.passwd is not None:
            user_pass = base64.b64encode('%s:%s' % (self.user, self.passwd))
            hdrs['Authorization'] = 'Basic %s' % user_pass
        self._connection.request(method, self.path, body = body,
                                 headers = hdrs)
        resp = self._connection.getresponse()
        if resp.status != 200:
            raise ResponseError(resp.status, resp.reason, resp.msg, resp)
        return resp

