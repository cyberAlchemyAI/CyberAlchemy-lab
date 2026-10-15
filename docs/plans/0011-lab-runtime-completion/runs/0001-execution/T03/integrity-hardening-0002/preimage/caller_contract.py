"""Trusted caller companion; select only immediately after exact captured load.

The caller independently pins this companion and the helper's exact bytes and
retains the returned contract outside the helper. No API payload creates it.
This is a bounded integrity contract, not isolation from arbitrary privileged
rewriting of the caller itself, its anchors, or the entire Python process.
"""
from types import FunctionType

def select(module,*,expected_path,expected_sha256):
    if module.__file__!=str(expected_path) or module._PIN!=expected_sha256:
        raise ValueError('independently captured helper origin differs')
    functions=list(module._CALLBACKS)+[module._SCOPE_BODY,module._check_integrity_state]
    records=tuple((fn,fn.__code__,fn.__globals__,fn.__defaults__,fn.__kwdefaults__,
        tuple(sorted((fn.__kwdefaults__ or {}).items())),fn.__closure__,
        tuple(cell.cell_contents for cell in (fn.__closure__ or ()))) for fn in functions)
    namespace=module.__dict__
    globals_selected=tuple(namespace.items())
    return module,expected_sha256,records,namespace,globals_selected

def check(contract,module):
    selected,pin,records,namespace,global_bindings=contract
    if module is not selected or module.__dict__ is not namespace:
        raise ValueError('capture helper module identity changed')
    if set(namespace)!={name for name,value in global_bindings}:
        raise ValueError('capture helper global names changed')
    for name,value in global_bindings:
        if namespace[name] is not value:raise ValueError('capture helper global binding changed')
    for fn,code,global_namespace,defaults,kwdefaults,kwitems,closure,cells in records:
        if (type(fn) is not FunctionType or fn.__code__ is not code or fn.__globals__ is not global_namespace
            or fn.__defaults__ is not defaults or fn.__kwdefaults__ is not kwdefaults
            or tuple(sorted((fn.__kwdefaults__ or {}).items()))!=kwitems or fn.__closure__ is not closure
            or any(cell.cell_contents is not value for cell,value in zip(fn.__closure__ or (),cells))):
            raise ValueError('capture helper function code or context changed')
    # The original guard object and code were checked before this call.
    records[9][0](pin)
