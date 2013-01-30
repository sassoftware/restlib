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
