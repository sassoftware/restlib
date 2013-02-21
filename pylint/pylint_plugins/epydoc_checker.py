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


from logilab import astng

from pylint.interfaces import IASTNGChecker
from pylint.checkers import BaseChecker

from epydoc.markup import epytext

class EpyTextNode(object):
    def __init__(self, docString):
        docNode = epytext.parse(docString)
        self.docNode = docNode
        self.docString = docString

    def getDocumentedParameters(self):
        fields = self.getChild('fieldlist')
        params = []
        if not fields:
            return params
        for field in fields.children:
            tag = self.getChild('tag', field)
            if tag:
                tag = tag.children[0]
                if tag == 'param':
                    paramName = self.getChild('arg', field).children[0]
                    params.append(paramName)
                elif tag in ('type', 'return', 'rtype', 'raise'):
                    continue
                else:
                    raise NotImplementedError("don't know how to handle tag '%s'" %tag)
            else:
                raise NotImplementedError("no tag found")
        return params

    def getChild(self, tag, docNode=None):
        if docNode is None:
            docNode = self.docNode
        for child in docNode.children:
            if child.tag == tag:
                return child

class EpydocParamsMatchChecker(BaseChecker):
    name = 'epydoc'
    msgs = {'C0999': ('Documented parameters do not match actual parameters',
                      'Used the parameters listed in epytext for a function'
                      ' do not match the actual parameter names')}
    options = ()
    __implements__ = IASTNGChecker


    def visit_function(self, node, *args, **kw):
        if node.doc is None:
            return
        # Ignore functions that look like slots. If we had a list of
        # all slot methods that we could import, that would be better,
        # but it seems it's only accessible from C.
        if node.name.startswith('__') and node.name.endswith('__'):
            return

        docParams = EpyTextNode(node.doc).getDocumentedParameters()
        if node.is_method() and node.type != 'staticmethod':
            neededParams = node.argnames[1:]
        else:
            neededParams = node.argnames
        # remove intentionally ignored arguments in common signatures
        neededParams = [x for x in neededParams if x != '_']
        if docParams != neededParams:
            self.add_message('C0999', node=node)

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(EpydocParamsMatchChecker(linter))
