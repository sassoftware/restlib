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
import sys

from restlib.response import Response
from restlib.http import request

class ExceptionCallback(object):
    def processException(self, request, excClass, exception, tb):
        import traceback
        content = ['%s: %s\nTraceback:\n' % (excClass.__name__, exception)]
        content.extend(traceback.format_tb(tb))
        return Response(status=500, content=''.join(content))

class HttpHandler(object):
    requestClass = request.Request

    def __init__(self, controller, requestClass=None, logger = None):
        self._controller = controller
        if requestClass:
            self.requestClass = requestClass
        self._logger = logger
        self._processRequest = []
        self._processMethod = []
        self._processResponse = []
        self._processException = []
        self.addCallback(ExceptionCallback())

    def setLogger(self, logger):
        self._logger = logger

    def addCallback(self, callback):
        for attr in ('processRequest', 'processMethod',
                     'processResponse', 'processException'):
            method = getattr(callback, attr, None)
            if method:
                getattr(self, '_' + attr).append(method)

    def getResponse(self, request):
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
            for processMethod in self._processRequest:
                response = processMethod(request)
                if response:
                    return response
            viewMethod, remainder, args, kw = self._controller.getView(
                                                        request.method,
                                                        request.unparsedPath)
            # NOTE: the above could be cached pretty easily.
            request.unparsedPath = remainder
            for processMethod in self._processMethod:
                response = processMethod(request, viewMethod, args, kw)
                if response:
                    return response
            response = viewMethod(request, *args, **kw)
        except KeyboardInterrupt:
            raise
        except NotImplementedError:
            response = Response(status=404)
        except Exception, e:
            ei = sys.exc_info()
            self._logger.error("500", exc_info = ei)
            # callbacks called first before the method get called
            # last afterwards
            for processMethod in reversed(self._processException):
                response = processMethod(request, *ei)
                if response:
                    return response
            return Response(status=500)
        return response

