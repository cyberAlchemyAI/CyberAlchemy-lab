"""Pure fail-closed generated-role read hardening for the external root.

This replaces the repository-root assumption in the frozen hardener with a
RootBoundCapture read scope. It does not install that scope or grant effects.
"""
from __future__ import annotations

import ast

from .path_contract import require


def _function(text: str, name: str, replacement: str) -> str:
    nodes = [node for node in ast.parse(text).body
             if isinstance(node, ast.FunctionDef) and node.name == name]
    require(len(nodes) == 1, 'exact original hardener function required: ' + name)
    node = nodes[0]
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno - 1]) + replacement + '\n' + ''.join(lines[node.end_lineno:])


def _once(text: str, old: str, new: str) -> str:
    require(text.count(old) == 1, 'explicit hardener preimage differs: ' + old[:64])
    return text.replace(old, new)


def harden(role: str, filename: str, text: str) -> str:
    """Apply only exact original source/reader/mapper/Context read deltas."""
    if role == 'source' and filename == 'base.py':
        text = _function(text, 'original', '''def original(row):
    from _t35_external_runtime_capture import read
    return read(row)''')
        text = _function(text, 'verify_source', '''def verify_source(pin):
    raw=original({'path':_t35_binding_path(HERE/'source-manifest.json'),'sha256':pin})
    m=parse(raw);require(m['authority_effect']=='none' and m['actual_owner_outcome'] is None,'source cannot grant authority')
    require(m['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'selected source environment differs')
    verify_inputs(m['files'])
    return m''')
        marker = 'def emit(path,value,*,raw=None):'
        require(text.count(marker) == 1, 'source emit declaration differs')
        text = text.replace(marker, '''def verify_inputs(rows,*,selected_external=()):
    from _t35_external_runtime_capture import verify_inputs as selected_verify
    return selected_verify(rows,selected_external=selected_external)
\n''' + marker)
    if role == 'reader' and filename == 'reader.py':
        text = _once(text, "        for row in manifest['files']:original(row)",
                     "        B.verify_inputs(manifest['files'])")
        text = _once(text,
                     "        require(sha(path.read_bytes())==self.adapter_pin,'independent current source adapter pin differs')\n        manifest=load(path)",
                     "        manifest=parse(original({'path':_t35_binding_path(path),'sha256':self.adapter_pin}))")
    if role == 'mapped' and filename == 'base.py':
        text = _once(text, "    for row in m['files']:original(row)",
                     "    reader.adapter.source.B.verify_inputs(m['files'])")
        text = _once(text,
                     "    require(sha(path.read_bytes())==pin,'independent current native mapper source differs')\n    m=load(path)",
                     "    m=source.parse(original({'path':_t35_binding_path(path),'sha256':pin}))")
    if role == 'context' and filename == 'base.py':
        text = _once(text, "    for row in m['files']:dependency_input_bytes(row,external)",
                     "    reader.adapter.source.B.verify_inputs(m['files'],selected_external=external)")
        text = _once(text,
                     "    require(sha((HERE/'source-manifest.json').read_bytes())==pin,'independent original Context delivery source pin differs');m=load(HERE/'source-manifest.json')",
                     "    m=reader.adapter.source.parse(original({'path':_t35_binding_path(HERE/'source-manifest.json'),'sha256':pin}))")
        text = _function(text, 'dependency_input_bytes', '''def dependency_input_bytes(row,selected_external):
    from _t35_external_runtime_capture import read
    require(row in selected_external or not Path(row['path']).is_absolute(),
            'external dependency input not explicitly selected')
    return read(row)''')
    if role == 'mapped' and filename == 'build.py':
        text = _once(text,
                     '    p=subprocess.run([str(EXE),*map(str,args)],capture_output=True,timeout=30)',
                     '    from _t35_external_runtime_capture import run_native\n    p=run_native(list(map(str,args)))')
    ast.parse(text)
    return text
