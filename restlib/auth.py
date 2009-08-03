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
"""
Contains BasicAuthCallback, a simple authentication callback.  Without
subclassing, it attaches (name, password) to the request object.  A subclass
could use the processRequest method to authenticate the user's information.
"""
import base64

from restlib import response

class BasicAuthCallback(object):

    def getAuth(self, request):
        """
        Parses the standard auth headers.
        """
        if not 'Authorization' in request.headers:
            return None
        type, user_pass = request.headers['Authorization'].split(' ', 1)
        user_name, password = base64.decodestring(user_pass).split(':', 1)
        return (user_name, password)

    def processRequest(self, request):
        """
        Callback hook, called by restlib.
        """
        auth = self.getAuth(request)
        request.auth = auth
        return self.processAuth(request)

    def processAuth(self, request):
        """
        Hook for extending BasicAuthCallback.  If the user cannot be
        authenticated, a Response object can be returned here to stop
        the calling of other methods.
        """
        return None
