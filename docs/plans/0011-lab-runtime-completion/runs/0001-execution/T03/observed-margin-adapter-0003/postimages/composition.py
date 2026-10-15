"""New private Root composition with independently captured helper seed bytes.

Root must supply four immutable records from its independently selected closed
startup capture. No helper chooses its own initial source bytes or code pins.
"""
import ast,hashlib,types
from pathlib import Path

def compose(host,parent,modules,expected_attachment,*,control_root,root_identity,selection_binding,helper_capture):
    api=Path(modules['service'].__file__).parent
    if type(helper_capture) is not tuple or len(helper_capture)!=4:raise ValueError('independent captured margin seed required')
    bodies={};helpers={}
    for record in helper_capture:
        if type(record) is not tuple or len(record)!=5:raise ValueError('closed captured helper record required')
        name,module,path,pin,raw=record
        if name not in ('observed_margin','margin_capture','margin_kernel','margin_seal') or name in helpers:raise ValueError('exact captured helper set required')
        expected=api/(name+'.py')
        if type(module) is not types.ModuleType:raise ValueError('captured helper must be actual module')
        if module is not modules[name] or module.__file__!=str(expected) or path!=str(expected) or type(raw) is not bytes or hashlib.sha256(raw).hexdigest()!=pin:
            raise ValueError('captured helper object/origin/bytes differ')
        references={}
        pending=[compile(raw,path,'exec')]
        while pending:
            code=pending.pop();references[code.co_qualname]=code
            pending.extend(value for value in code.co_consts if type(value) is types.CodeType)
        # Required exports/methods come from captured source, never a live
        # callable's mutable __module__ marker. Validate before any helper call.
        functions=[]
        for declaration in ast.parse(raw).body:
            if isinstance(declaration,(ast.FunctionDef,ast.AsyncFunctionDef)):
                functions.append((declaration.name,vars(module).get(declaration.name),declaration,None))
            elif isinstance(declaration,ast.ClassDef):
                owner=vars(module).get(declaration.name)
                if type(owner) is not type or owner.__module__!=module.__name__:raise ValueError('source-defined helper class differs')
                for method in declaration.body:
                    if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        functions.append((declaration.name+'.'+method.name,vars(owner).get(method.name),method,owner))
        for qualified,function,declaration,owner in functions:
            reference=references.get(qualified)
            if (type(function) is not types.FunctionType or reference is None or function.__qualname__!=qualified
                or function.__module__!=module.__name__ or function.__globals__ is not vars(module)
                or function.__builtins__ is not (vars(module)['__builtins__'] if type(vars(module)['__builtins__']) is dict else vars(vars(module)['__builtins__']))
                or function.__code__!=reference or function.__code__.co_filename!=path):
                raise ValueError('source-defined helper callable/context differs before seed factory')
            if function.__code__.co_freevars:
                if function.__code__.co_freevars!=('__class__',) or function.__closure__ is None or len(function.__closure__)!=1 or function.__closure__[0].cell_contents is not owner:
                    raise ValueError('source-defined helper closure differs')
            elif function.__closure__ is not None:raise ValueError('unexpected helper closure')
            # Defaults in these selected sources are constant literals/arithmetic;
            # compile in an empty builtin context, without evaluating live aliases.
            defaults=tuple(eval(compile(ast.Expression(value),path,'eval'),{'__builtins__':{}}) for value in declaration.args.defaults)
            kwdefaults={arg.arg:eval(compile(ast.Expression(value),path,'eval'),{'__builtins__':{}}) for arg,value in zip(declaration.args.kwonlyargs,declaration.args.kw_defaults) if value is not None}
            if function.__defaults__!=(defaults or None) or function.__kwdefaults__!=(kwdefaults or None):raise ValueError('helper defaults differ before seed')
        required={'margin_seal':'make_guard','observed_margin':'bind_runtime'}.get(name)
        if required is not None and not any(q==required for q,fn,d,o in functions):raise ValueError('required factory absent from captured source')
        helpers[name]=module;bodies[name]=raw
    if set(helpers)!=set(('observed_margin','margin_capture','margin_kernel','margin_seal')):raise ValueError('captured helper set incomplete')
    margin=helpers['observed_margin']
    if margin.C is not helpers['margin_capture'] or margin.K is not helpers['margin_kernel'] or margin.L is not helpers['margin_seal']:raise ValueError('captured helper import context differs')
    seal=helpers['margin_seal'].make_guard(helpers,bodies)
    seal[0]()
    margin=helpers['observed_margin']
    return margin.bind_runtime(host,parent,{name:modules[name] for name in margin.MODULES},
                               control_root,root_identity,selection_binding,expected_attachment,seal)
