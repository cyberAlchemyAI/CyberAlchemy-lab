"""Native-only original container/body/authority scope correspondence."""
import copy
from pathlib import Path
from .protocol import ROOT,HERE
from .handlers import cut
from .workflow_output_contracts import need,closed,parse,sha

PROOF_FIELDS=('schema_version','artifact','container_scope_ref','body_scope_ref','authority_scope_ref','review_sha256','source_binding','source_cut','principal_ref','work_ref','producer_binding','producer_entrypoint','authority_effect')
class ScopeContracts:
    def __init__(self,host,plan):
        self.host=host;self.plan=copy.deepcopy(plan);self.contracts={};self.bindings={}
        for ref,row in plan['transitions'].items():
            selected=row['scope_contract_binding'];native=row['producer_binding']['path']==str((HERE/'workflow_native_outputs.py').relative_to(ROOT)) and row['producer_entrypoint']=='NativeTypedResultAdapter.capture'
            need(native or selected is None,'scope differences require the exact selected native output adapter')
            if not native:continue
            need(selected is not None,'native scope contract must be independently selected')
            raw=host.vault.material(selected);need(sha(raw)==selected['sha256'],'private native scope contract changed');p=parse(raw)
            closed(p,('schema_version','producer_binding','producer_entrypoint','review_sha256','source_binding','source_cut','principal_ref','work_ref','container_scope_ref','authority_scope_ref','permitted_body_scope_refs','authority_effect'))
            need(p['schema_version']=='lab-private-native-workflow-scope/v1-candidate' and p['authority_effect']=='none','exact private native scope contract required')
            from jsonschema import Draft202012Validator
            Draft202012Validator(parse((HERE/'workflow-native-scope.schema.json').read_bytes())).validate(p)
            control=parse(host.vault.material(row['producer_control_binding']));need(sha(host.vault.material(row['producer_control_binding']))==row['producer_control_binding']['sha256'],'native producer selection changed')
            b=p['producer_binding'];closed(b,('path','sha256'));path=Path(b['path'])
            need(path.is_absolute() and b['path']==path.as_posix() and '..' not in path.parts and '\\' not in b['path'] and '\0' not in b['path'] and str(path)==str(ROOT/Path(control['capability_binding']['path'])) and b['sha256']==control['capability_binding']['sha256'] and p['producer_entrypoint']==control['capability_entrypoint'],'scope contract must bind exact actual native producer origin')
            need(p['source_cut']==plan['source_cut'] and p['principal_ref']==plan['principal_ref'] and p['container_scope_ref']==row['output_scope_ref'],'scope contract current principal/cut/header scope differs')
            self.contracts[ref]=copy.deepcopy(p);self.bindings[ref]=copy.deepcopy(selected)
    def validate(self,ref,artifact,body_scope,proof):
        need(ref in self.contracts,'native scope contract unavailable');p=self.contracts[ref];selected=self.bindings[ref]
        need(sha(self.host.vault.material(selected))==selected['sha256'] and self.plan['source_cut']==cut(self.host.handlers.view) and self.host.channel.guard()['principal_ref']==p['principal_ref'],'native scope contract/current source changed')
        closed(proof,PROOF_FIELDS)
        need(proof['schema_version']=='lab-original-native-record-scope/v1-candidate' and proof['authority_effect']=='none' and proof['artifact']==artifact,'actual native scope proof/header differs')
        for key in ('producer_binding','producer_entrypoint','review_sha256','source_binding','source_cut','principal_ref','work_ref','container_scope_ref','authority_scope_ref'):need(proof[key]==p[key],'native source-backed scope correspondence differs: '+key)
        need(artifact['scope_ref']==p['container_scope_ref'] and body_scope==proof['body_scope_ref'] and body_scope in p['permitted_body_scope_refs'],'original body scope lacks exact selected native correspondence')
        need(p['container_scope_ref'] in self.host.channel.policy_guard()['scope_refs'],'original header scope permission absent')
        return True
