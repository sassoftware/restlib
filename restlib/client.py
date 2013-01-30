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


import base64
import httplib
import urllib

from conary.lib import util

class ConnectionError(Exception):
    pass

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
        self.hostport = None
        self.path = None
        self.headers = headers or {}

        urltype, url = urllib.splittype(url)
        if urltype:
            self.scheme = urltype.lower()

        host, self.path = urllib.splithost(url)
        if host:
            user_passwd, self.hostport = urllib.splituser(host)
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
        self._connection = cls(self.hostport)
        try:
            self._connection.connect()
        except httplib.socket.error, e:
            raise ConnectionError(str(e))
        return self

    def request(self, method, body=None, headers=None, contentLength=None,
            callback=None):
        hdrs = self.headers.copy()
        hdrs.update(headers or {})
        if self.user is not None and self.passwd is not None:
            user_pass = base64.b64encode('%s:%s' % (self.user, self.passwd))
            hdrs['Authorization'] = 'Basic %s' % user_pass
        if hasattr(body, "read"):
            # We need to stream
            if contentLength is None:
                # Determine body size
                body.seek(0, 2)
                contentLength = body.tell()
                body.seek(0, 0)
            hdrs['Content-Length'] = str(contentLength)
            self._connection.putrequest(method, self.path)
            for hdr, value in hdrs.iteritems():
                self._connection.putheader(hdr, value)
            self._connection.endheaders()
            util.copyfileobj(body, self._connection, sizeLimit=contentLength,
                callback=callback)
        else:
            self._connection.request(method, self.path, body = body,
                                     headers = hdrs)
        resp = self._connection.getresponse()
        if resp.status != 200:
            raise ResponseError(resp.status, resp.reason, resp.msg, resp)
        return resp
