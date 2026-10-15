"""Independently captured module origins and original executable membership."""
import ast,inspect,sys,types,importlib.util
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
        self.aliases=[];self.literals=[];self.wildcards=[]
        selected_modules={id(row[0])for row in self.expected}
        for module,binding,raw,names,table in self.expected:
            for node in ast.parse(raw).body:
                if isinstance(node,ast.ImportFrom)and node.module:
                    name=importlib.util.resolve_name('.'*node.level+node.module,module.__package__)if node.level else node.module
                    imported=sys.modules.get(name);need(imported is not None,'selected imported provider absent')
                    origin=getattr(imported,'__file__',None)
                    # Every repository Python provider must be selected, rather
                    # than trusting a matching alias in an unselected module.
                    if origin and Path(origin).is_relative_to('/home/vlad_/projects/CyberAlchemy-lab'):
                        need(id(imported)in selected_modules or '/installations/0004/'in str(origin),'repository provider outside independent executable closure')
                    for alias in node.names:
                        if alias.name=='*':
                            exports=tuple(getattr(imported,'__all__',tuple(k for k in imported.__dict__ if not k.startswith('_'))))
                            need(all(type(k)is str for k in exports),'closed captured wildcard export names required')
                            self.wildcards.append((imported,exports))
                            self.aliases.extend((module,k,imported,k)for k in exports)
                        else:self.aliases.append((module,alias.asname or alias.name,imported,alias.name))
                elif isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
                    try:value=ast.literal_eval(node.value)
                    except (ValueError,TypeError):continue
                    self.literals.append((module,node.targets[0].id,value))
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
        for provider,exports in self.wildcards:
            current=tuple(getattr(provider,'__all__',tuple(k for k in provider.__dict__ if not k.startswith('_'))))
            need(current==exports,'captured provider wildcard membership differs')
        for module,name,provider,export in self.aliases:
            need(getattr(module,name)is getattr(provider,export),'selected imported helper alias differs')
        for module,name,value in self.literals:
            need(type(getattr(module,name))is type(value)and getattr(module,name)==value,'selected literal module context differs')
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
