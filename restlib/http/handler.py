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


import sys
import traceback

from restlib.response import Response
from restlib.http import request

class ExceptionCallback(object):
    """
        Debugging exception callback.  Simply displays the traceback to the
        webbrowser.
    """

    def processException(self, request, excClass, exception, tb):
        content = ['%s: %s\nTraceback:\n' % (excClass.__name__, exception)]
        content.append(''.join(traceback.format_tb(tb)))
        return Response(status=500, content=''.join(content))

class HttpHandler(object):
    """
    Base HttpHandler.  This class (through its http server-specific sublasses)
    is the entry point for restlib.

    The Handler class should be instantiated once and used for multiple
    requests.  Each http server handler will convert its request class into a
    restlib request.Request.  That request will be passed into getResponse, and
    the result will be a response.Response class.  The http server handler
    will convert the request back into its server-specific response.

    @param controller: the site-level controller to use to parse requests.
    This should be an instantiation of a control object, and should not have
    any request-specific data in it.

    @param requestClass: the specific requestClass to associate with this
    handler (used by subclasses).

    @param logger: python's logging-style logger.  Only used internally to log
    exceptions.
    """
    requestClass = request.Request
    exceptionCallback = ExceptionCallback

    def __init__(self, controller, requestClass=None, logger = None):
        self._controller = controller
        if requestClass:
            self.requestClass = requestClass
        self._logger = logger
        self._processRequest = []
        self._processMethod = []
        self._processResponse = []
        self._processException = []
        if self.exceptionCallback:
            self.addCallback(self.exceptionCallback())

    def setLogger(self, logger):
        self._logger = logger

    def addCallback(self, callback):
        """
        Adds a callback instance that will be called during the processing of
        each request at particular times depending on what methods are
        defined in the instance.  For example, if the instance has a
        "processMethod" method, then it will be used as a processMethod
        callback.  A single callback instance can provide multiple methods.

        A callback can return either None or a Response object.  
        The following callbacks currently are supported:

        processRequest: called immediately after the request is received by
        the hander.  Called with the request object as a parameter.  If
        multiple callbacks are associated with processRequest, they are
        called in the order in which they were added.  If a callback
        returns anything other than None, it will be treated as a response
        object, and no further attempt to route the request will be made.
        Instead, the processResponse callbacks will be called immediately.

        processMethod: called after the view to be called has been determined.
        Arguments: request, view method, positional arguments and key word
        arguments to be passed into the view.
        This callback is often used to do common setup that is needed before a
        view can be called, for example, if a keyword needs to be added to
        a request, it can be added to the kwargs dictionary that is passed in.
        If a processMethod returns anything other than None, it is assumed to
        be a Response object and no further attempt to route the request
        will be made and the viewMethod will not be called.  Callbacks are
        called in the order in which they are added.

        processResponse: called after a response has been generated, either
        after calling a viewMethod or after a response returned from an
        earlier callback.
        Arguments: the request object and the response object.  If a new
        response is returned, it will be used as the response object.  Unlike
        the previous callbacks, _all_ processResponse callbacks will be
        called on a response, even if an earlier callback returns a Response
        object instead of None.  Also, callbacks are called in the reverse
        order in which they are added.  The reason for this reversal is that
        it puts the first callback added in a primary position for both
        the processRequest and processResponse callbacks: it will be the
        first callback called when calling processRequest; if it returns a
        Response object then no other processing will be done.  It will be the
        last callback called when calling processResponse, which means that
        it controls the final response that is returned.

        processException: called when an exception is raised anywhere during
        routing, rendering or callbacks.  Not called if the exception is
        NotImplementedError (this is automatically converted to a 404) or
        KeyboardException.
        Arguments: request, exception class, exception, traceback object.
        Like processResponse, called in the reverse of the order in which
        they are added.  If an exception callback returns a response, that
        response will be used as the response to the exception.
        """
        for attr in ('processRequest', 'processMethod',
                     'processResponse', 'processException'):
            method = getattr(callback, attr, None)
            if method:
                getattr(self, '_' + attr).append(method)

    def getResponse(self, request):
        request.rootController = self._controller
        response = self.getInitialResponse(request)
        # callbacks called first before the method get called
        # last afterwards
        for callbackMethod in reversed(self._processResponse):
            new_response = callbackMethod(request, response)
            if new_response:
                response = new_response
        return response

    def getInitialResponse(self, request):
        try:
            for callback in self._processRequest:
                response = callback(request)
                if response:
                    return response
            viewMethod, remainder, args, kw = self._controller.getView(
                                                        request.method,
                                                        request.unparsedPath)
            # NOTE: the above could be cached pretty easily.
            request.unparsedPath = remainder
            for callback in self._processMethod:
                response = callback(request, viewMethod, args, kw)
                if response:
                    return response
            response = viewMethod(request, *args, **kw)
        except KeyboardInterrupt:
            raise
        except NotImplementedError:
            response = Response(status=404)
        except Exception, e:
            ei = sys.exc_info()
            # callbacks called first before the method get called
            # last afterwards
            for callback in reversed(self._processException):
                response = callback(request, *ei)
                if response:
                    return response
            if self._logger:
                self._logger.error("500", exc_info = ei)
            return Response(status=500)
        return response
