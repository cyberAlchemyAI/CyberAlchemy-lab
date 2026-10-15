"""New private Root composition with independently captured helper seed bytes.

Root must supply four immutable records from its independently selected closed
startup capture. No helper chooses its own initial source bytes or code pins.
"""
import hashlib,types
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
        if module is not modules[name] or module.__file__!=str(expected) or path!=str(expected) or type(raw) is not bytes or hashlib.sha256(raw).hexdigest()!=pin:
            raise ValueError('captured helper object/origin/bytes differ')
        references={}
        pending=[compile(raw,path,'exec')]
        while pending:
            code=pending.pop();references[code.co_qualname]=code
            pending.extend(value for value in code.co_consts if type(value) is types.CodeType)
        functions=[]
        for value in vars(module).values():
            if type(value) is types.FunctionType and value.__module__==module.__name__:functions.append(value)
            elif isinstance(value,type) and value.__module__==module.__name__:
                functions.extend(fn for fn in vars(value).values() if type(fn) is types.FunctionType)
        for function in functions:
            reference=references.get(function.__qualname__)
            if reference is None:
                raise ValueError('unselected helper callable')
            if function.__code__!=reference or function.__code__.co_filename!=path:raise ValueError('helper callable differs before seed factory')
        helpers[name]=module;bodies[name]=raw
    if set(helpers)!=set(('observed_margin','margin_capture','margin_kernel','margin_seal')):raise ValueError('captured helper set incomplete')
    seal=helpers['margin_seal'].make_guard(helpers,bodies)
    seal[0]()
    margin=helpers['observed_margin']
    return margin.bind_runtime(host,parent,{name:modules[name] for name in margin.MODULES},
                               control_root,root_identity,selection_binding,expected_attachment,seal)
