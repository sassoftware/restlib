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


class PublicApiChecker(BaseChecker):
    name = 'apicheck'
    msgs = {'C1000': ('Used private conary %s %s',
                      'Used private api call')}
    options = ()
    __implements__ = IASTNGChecker

    def visit_from(self, node):
        name_parts = node.modname.split('.')
        module = node.root().import_module(name_parts[0])
        if module != 'conary':
            return
        name_parts = node.modname.split('.')
        obj = self._follow_imports(node, module, name_parts[1:])
        if not isinstance(obj, astng.Module):
            self.check_public(obj)
        else:
            module = obj

        for name, _ in node.names:
            if name == '*':
                continue
            obj = self._follow_imports(node, module, name.split('.'))
            if not isinstance(obj, astng.Module):
                self.check_public(node, obj)

    def _follow_imports(node, module, module_names):
        assert isinstance(module, astng.Module), module
        while module_names:
            name = module_names.pop(0)
            if name == '__dict__':
                module = None
                break
            else:
                module = module.getattr(name)[0].infer().next()
        return module

    def is_function_public(self, node):
        if node.decorators:
            for decorator in node.decorators:
                moduleName = decorator.infer().next().root().name
                if moduleName == 'conary.lib.api':
                    # any api marking states that this thing is avialable
                    return True
        return False

    def is_class_public(self, node):
        if (not node.name.startswith('_') and
            (self.marked_public(node.root()) or self.marked_public(node))):
            return True
        for method in node.methods():
            if self.is_function_public(method):
                return True
        return False

    def marked_public(self, node):
        for apiType in '__developer_api__', '__public_api__':
            try:
                node.getattr(apiType)
                return True
            except astng.NotFoundError:
                pass
        return False

    def check_public(self, statement, node):
        if isinstance(node, astng.Function):
            if (node.is_method() and
                (not node.name[0] == '_' or (
                    node.name[0:2] == '__' and node.name[-2:] == '__'))):
                classNode = node.parent.parent
                if (self.marked_public(classNode) 
                    or self.marked_public(node.root())):
                    return
            if not self.is_function_public(node):
                objType, nodeName = self.get_node_name(node)
                if nodeName == 'dict.itervalues':
                    import epdb
                    epdb.st()
                self.add_message('C1000', node=statement.statement(),
                                args=(objType, nodeName))
        elif isinstance(node, astng.Class):
            if not self.is_class_public(node):
                objType, nodeName = self.get_node_name(node)
                self.add_message('C1000', node=statement.statement(),
                                args=(objType, nodeName))
        elif isinstance(node, astng.Yes):
            pass
        else:
            import epdb
            epdb.st()

    def get_node_name(self, node):
        objType = node.__class__.__name__.split('.')[-1].lower()
        parent = node.parent
        while isinstance(parent, astng.Stmt):
            parent = parent.parent
        parentName = parent.name
        nodeName = node.name
        return objType, '%s.%s' % (parentName, nodeName)


    def visit_getattr(self, node):
        try:
            source = node.expr.infer().next()
        except astng.InferenceError, e:
            return
        except astng.NotFoundError, e:
            return
        if isinstance(source, (astng.Yes, astng.Dict)):
            return
        moduleName = source.root().name
        if not moduleName.startswith('conary.'):
            return
        try:
            object = source.getattr(node.attrname)[0].infer().next()
        except astng.InferenceError, e:
            return
        except astng.NotFoundError, e:
            return
        else:
            self.check_public(node, object)

def register(linter):
    """required method to auto register this checker"""
    linter.register_checker(PublicApiChecker(linter))
