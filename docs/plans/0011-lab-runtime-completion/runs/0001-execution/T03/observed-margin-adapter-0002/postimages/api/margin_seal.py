"""Captured helper graph seal. No original callback replacement or effects.

The caller checks the guard's held code/default/context before executing it.
The guard uses an isolated empty global context and captured builtins. Its
immutable node selections are private startup products, never API inputs.
"""
import ast,builtins,types
from pathlib import Path

def snapshot(value):
    t=type(value)
    if t in (str,bytes,int,float,complex,bool,type(None)):return (t,value)
    if t in (tuple,list):return (t,tuple(snapshot(v) for v in value))
    if t is dict:return (t,tuple(sorted(((snapshot(k),snapshot(v)) for k,v in value.items()),key=repr)))
    if t in (set,frozenset):return (t,tuple(sorted((snapshot(v) for v in value),key=repr)))
    if isinstance(value,Path):return (Path,str(value))
    return ('identity',id(value))

def _check(nodes,fields,module_members,library_members,class_members,contexts,namespaces,_snapshot,_type,_FunctionType,_getattr,_vars,_ValueError):
    # First compare every callable code and namespace binding. Only after that
    # use the independently held snapshot helper to compare mutable constants,
    # defaults and keyword-default contents. No runtime argument/frame reads.
    for function,code,defaults,default_value,kwdefaults,kwvalue,closure,cells,globals in nodes:
        if function.__code__ is not code or function.__defaults__ is not defaults or function.__kwdefaults__ is not kwdefaults or function.__closure__ is not closure or function.__globals__ is not globals:
            raise _ValueError('selected margin helper callable changed')
        if closure is not None:
            if len(closure)!=len(cells) or any(cell.cell_contents is not value for cell,(value,expected) in zip(closure,cells)):
                raise _ValueError('selected margin helper closure changed')
    for owner,keys in namespaces:
        if tuple(sorted(_vars(owner)))!=keys:raise _ValueError('selected margin helper namespace changed')
    for owner,key,value in class_members:
        if _vars(owner).get(key) is not value:raise _ValueError('selected margin library descriptor changed')
    for owner,key,value in module_members+library_members+contexts:
        if _getattr(owner,key,None) is not value:raise _ValueError('selected margin helper alias changed')
    for function,code,defaults,default_value,kwdefaults,kwvalue,closure,cells,globals in nodes:
        if _snapshot(defaults)!=default_value or _snapshot(kwdefaults)!=kwvalue:raise _ValueError('selected margin helper defaults changed')
        if closure is not None and any(_snapshot(cell.cell_contents)!=expected for cell,(value,expected) in zip(closure,cells)):
            raise _ValueError('selected margin helper closure contents changed')
    for owner,key,value,expected in fields:
        if _snapshot(_getattr(owner,key,None))!=expected:raise _ValueError('selected margin helper constant changed')
    return None

# Empty guard globals require every executed builtin in its held defaults.
# len/any/zip are explicitly captured too; they are not dynamic module globals.
def guard_context():return {'__builtins__':{'len':len,'any':any,'zip':zip,'tuple':tuple,'sorted':sorted}}

def literal_value(expression):
    try:return ast.literal_eval(expression)
    except (ValueError,TypeError):pass
    if isinstance(expression,ast.Call) and not expression.keywords and len(expression.args)==1 and isinstance(expression.func,ast.Name):
        if expression.func.id=='Path':return Path(ast.literal_eval(expression.args[0]))
        if expression.func.id=='set':return set(literal_value(expression.args[0]))
    if isinstance(expression,ast.Call) and not expression.args and not expression.keywords and isinstance(expression.func,ast.Attribute) and expression.func.attr=='split':
        value=ast.literal_eval(expression.func.value)
        if type(value) is str:return value.split()
    raise ValueError('not a source literal constant')

def make_guard(modules,source_bytes):
    functions=[];module_members=[];fields=[];library_members=[];class_members=[];contexts=[];namespaces=[];external_classes=set()
    selected_names={module.__name__ for module in modules.values()};all_names=set()
    for module in modules.values():
        for value in vars(module).values():
            if isinstance(value,types.FunctionType) and value.__module__==module.__name__:all_names.update(value.__code__.co_names)
            if isinstance(value,type) and value.__module__==module.__name__:
                for fn in vars(value).values():
                    if isinstance(fn,types.FunctionType):all_names.update(fn.__code__.co_names)
    for label,module in modules.items():
        path=Path(module.__file__);raw=source_bytes[label];compiled=compile(raw,str(path),'exec')
        def nested(code):
            yield code
            for item in code.co_consts:
                if isinstance(item,types.CodeType):yield from nested(item)
        expected={c.co_qualname:c for c in nested(compiled)}
        # Literal source-owned policy/checkpoint tables are checked against
        # independently captured AST, not a possibly altered live baseline.
        for statement in ast.parse(raw).body:
            if isinstance(statement,ast.Assign):
                for target in statement.targets:
                    if isinstance(target,ast.Name):
                        try:literal=literal_value(statement.value)
                        except (ValueError,TypeError):continue
                        if snapshot(getattr(module,target.id))!=snapshot(literal):raise ValueError('selected literal constant differs')
        namespaces.append((module,tuple(sorted(vars(module)))))
        for key,value in vars(module).copy().items():
            if key.startswith('__') and key not in {'__builtins__'}:continue
            module_members.append((module,key,value));fields.append((module,key,value,snapshot(value)))
            if isinstance(value,types.FunctionType) and value.__module__==module.__name__:functions.append(value)
            elif isinstance(value,type) and value.__module__==module.__name__:
                namespaces.append((value,tuple(sorted(vars(value)))))
                for name,item in vars(value).copy().items():
                    if name=='__dict__':continue # closed namespace keys checked above
                    module_members.append((value,name,item));fields.append((value,name,item,snapshot(item)))
                    if isinstance(item,types.FunctionType):functions.append(item)
                    elif isinstance(item,(staticmethod,classmethod)):functions.append(item.__func__)
            elif isinstance(value,type):external_classes.add(value)
            elif isinstance(value,types.ModuleType) and value.__name__ not in selected_names:
                for attr in all_names:
                    if attr in vars(value):
                        alias=getattr(value,attr);library_members.append((value,attr,alias))
                        if isinstance(alias,types.FunctionType):functions.append(alias)
        for function in functions:
            if function.__module__!=module.__name__:continue
            if function.__qualname__ in expected:
                # Independent built-in immutable code equality and exact origin;
                # never delegate this seed comparison to an unsealed helper.
                reference=expected[function.__qualname__]
                if function.__code__!=reference or function.__code__.co_filename!=str(path):raise ValueError('selected helper code differs from captured compile')
            else:raise ValueError('unselected helper callable')
            contexts.append((function,'__globals__',function.__globals__))
    for selected_class in external_classes:
        for base in selected_class.__mro__:
            namespaces.append((base,tuple(sorted(vars(base)))))
            for attr in all_names:
                if attr not in vars(base):continue
                descriptor=vars(base)[attr];class_members.append((base,attr,descriptor))
                if isinstance(descriptor,types.FunctionType):functions.append(descriptor)
                elif isinstance(descriptor,(classmethod,staticmethod)):functions.append(descriptor.__func__)
                elif isinstance(descriptor,property):
                    functions.extend(fn for fn in (descriptor.fget,descriptor.fset,descriptor.fdel) if isinstance(fn,types.FunctionType))
    nodes=[]
    for fn in dict.fromkeys(functions):
        nodes.append((fn,fn.__code__,fn.__defaults__,snapshot(fn.__defaults__),fn.__kwdefaults__,snapshot(fn.__kwdefaults__),fn.__closure__,
                      tuple((cell.cell_contents,snapshot(cell.cell_contents)) for cell in fn.__closure__) if fn.__closure__ else (),fn.__globals__))
    defaults=(tuple(nodes),tuple(fields),tuple(module_members),tuple(library_members),tuple(class_members),tuple(contexts),tuple(namespaces),snapshot,type,types.FunctionType,getattr,vars,ValueError)
    context=guard_context();guard=types.FunctionType(_check.__code__,context,'captured_margin_helper_guard',defaults)
    return guard,guard.__code__,guard.__defaults__,guard.__globals__,tuple(context['__builtins__'].items())
