"""Independently captured module origins and original executable membership."""
import ast,inspect,sys,types
from pathlib import Path
from .contracts import need,sha,closed

def codes(code):
    yield code
    for child in code.co_consts:
        if type(child)is types.CodeType:yield from codes(child)

class SelectedSoftware:
    def __init__(self,modules,read_public):
        # Each tuple comes from Root's independently selected, captured loader.
        # No expected pin is inferred from current files or public ingress.
        need(type(modules)is tuple and modules,'independent full captured module closure required')
        self.modules=modules;self.read_public=read_public;self.expected=[]
        for module,binding,raw in modules:
            closed(binding,('path','sha256'));need(type(raw)is bytes and sha(raw)==binding['sha256'],'independent captured source differs')
            path=Path(binding['path']);need(path.is_absolute() and '..' not in path.parts,'true absolute original module origin required')
            tree=ast.parse(raw);compiled=compile(raw,str(path),'exec',dont_inherit=True);code_table={c.co_qualname:c for c in codes(compiled)}
            names=[]
            def members(nodes,prefix=''):
                for node in nodes:
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        names.append((prefix+node.name,'function'))
                    elif isinstance(node,ast.ClassDef):
                        names.append((prefix+node.name,'class'));members(node.body,prefix+node.name+'.')
            members(tree.body)
            self.expected.append((module,binding,raw,names,code_table))
        self.guard()
    def guard(self):
        for module,binding,raw,names,table in self.expected:
            path=Path(binding['path']);need(sys.modules.get(module.__name__)is module and Path(module.__file__)==path,'selected module registration/origin differs')
            need(self.read_public(binding)==raw,'selected physical/captured source differs')
            for name,kind in names:
                value=module
                for part in name.split('.'):
                    value=inspect.getattr_static(value,part)
                    if isinstance(value,(staticmethod,classmethod)):value=value.__func__
                    if isinstance(value,property):value=value.fget
                if kind=='class':need(type(value)is type and value.__module__==module.__name__,'original selected class membership differs')
                else:need(type(value)is types.FunctionType and value.__globals__ is module.__dict__ and value.__code__==table[name], 'selected function code/context differs: '+name)
    def function(self,callback):
        function=getattr(callback,'__func__',callback)
        need(type(function)is types.FunctionType,'selected actual Python capability required')
        matches=[row for row in self.expected if function.__globals__ is row[0].__dict__]
        need(len(matches)==1,'capability globals outside independent closure')
        module,binding,raw,names,table=matches[0]
        need(function.__qualname__ in table and function.__code__==table[function.__qualname__], 'capability code/origin differs')
        if '<locals>' not in function.__qualname__:
            registered=module
            for part in function.__qualname__.split('.'):registered=getattr(registered,part)
            need(getattr(registered,'__func__',registered)is function,'capability registration differs')
        else:
            need(inspect.ismethod(callback) and type(callback.__self__).__module__==module.__name__, 'actual selected nested store method required')
        return callback
