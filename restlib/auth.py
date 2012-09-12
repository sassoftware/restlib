#
# Copyright (c) rPath, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
