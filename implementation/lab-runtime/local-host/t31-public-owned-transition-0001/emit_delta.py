"""Emit maintained Service postimage; never mutate an existing API cut."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def emit(base,out):
    out.mkdir(mode=0o700,parents=True,exist_ok=False)
    raw=(base/'service.py').read_bytes();text=raw.decode()
    old="    def select_workflow_transition(self,message,outer,key):\n"
    if text.count(old)!=1:raise ValueError('exact existing workflow selector signature required')
    text=text.replace(old,"    def workflow_handler_binding(self):\n        from .owned_workflow_transition import selected\n        leaf='owned_workflow_transition.py' if selected(self) is not None else 'workflow_transition.py'\n        return binding(str((HERE/leaf).relative_to(ROOT)),(HERE/leaf).read_bytes())\n\n    def select_workflow_transition(self,message,outer,key,deadline=None):\n",1)
    marker="            from .workflow_output_factory import reader_for_host\n            builder=WorkflowTransition"
    if text.count(marker)!=1:raise ValueError('exact existing workflow preclaim selector body required')
    text=text.replace(marker,"            from .owned_workflow_transition import select as select_owned\n            owned=select_owned(self,message,outer,key,deadline)\n            if owned is not None:return owned\n"+marker,1)
    call="self.select_workflow_transition(message,call['expected_source_cut'],call['idempotency_key'])"
    if text.count(call)!=1:raise ValueError('one actual common workflow dispatch required')
    text=text.replace(call,"self.select_workflow_transition(message,call['expected_source_cut'],call['idempotency_key'],effective)",1)
    handler="binding(str((HERE/'workflow_transition.py').relative_to(ROOT)),(HERE/'workflow_transition.py').read_bytes()) if call['operation']=='workflow.transition'"
    if text.count(handler)!=1:raise ValueError('one actual workflow handler binding required')
    text=text.replace(handler,"self.workflow_handler_binding() if call['operation']=='workflow.transition'",1)
    close="    def close(self):\n        try:\n"
    if text.count(close)!=1:raise ValueError('one actual Service close boundary required')
    text=text.replace(close,"    def close(self):\n        from .owned_workflow_transition import uninstall\n        uninstall(self)\n        try:\n",1)
    lines=text.splitlines(keepends=True);nodes=ast.parse(text)
    assignments=[n for n in ast.walk(nodes) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and t.attr=='code_files' for t in n.targets)]
    if len(assignments)!=1:raise ValueError('one actual Service code closure assignment required')
    n=assignments[0];lines.insert(n.end_lineno,"        self.code_files.update({name:source.sha((HERE/name).read_bytes()) for name in ('owned_workflow_transition.py','owned_workflow_semantics.py')})\n")
    changed=''.join(lines).encode();ast.parse(changed);(out/'service.py').write_bytes(changed)
    for name in ('owned_workflow_transition.py','owned_workflow_semantics.py'):(out/name).write_bytes((HERE/name).read_bytes())
    pins={'original_service':{'path':str(base/'service.py'),'sha256':sha(raw)},'postimages':{p.name:sha(p.read_bytes()) for p in sorted(out.iterdir())},
          'strict_WorkflowTransition_and_K_CURRENT_unchanged':True,'public_request_and_receipt_schemas_unchanged':True,
          'auth_delta_required':'CurrentLegacy transition only through owned_workflow_transition.validate_control; source control equals owned.source_bindings(). All ordinary strict workflow source cases preserved.'}
    (out/'DELTA-PINS.json').write_text(json.dumps(pins,indent=2,sort_keys=True)+'\n')
    return pins
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('base',type=Path);parser.add_argument('output',type=Path);a=parser.parse_args();print(json.dumps(emit(a.base,a.output),sort_keys=True))
