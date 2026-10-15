"""Explicit new private composition. Root closed capture supplies inputs.

No API payload can select a mode, policy, cut, load observation, software pin or
parent. A future driver must select this code and all postimages independently.
"""
from pathlib import Path

def compose(host,parent,modules,expected_attachment,*,control_root,root_identity,selection_binding):
    # Exact object supplied by the independently closed capture; no ordinary
    # import may substitute a previously cached absolute module.
    margin=modules['observed_margin']
    expected=Path(modules['service'].__file__).parent/'observed_margin.py'
    if Path(margin.__file__)!=expected or Path(margin.bind_runtime.__code__.co_filename)!=expected:
        raise ValueError('unselected margin composition origin')
    return margin.bind_runtime(host,parent,{name:modules[name] for name in margin.MODULES},
                               control_root,root_identity,selection_binding,expected_attachment)
