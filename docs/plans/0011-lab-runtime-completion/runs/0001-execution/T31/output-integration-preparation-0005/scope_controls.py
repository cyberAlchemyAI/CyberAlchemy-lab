"""Authored inert private scope-parser controls; run only after Root review."""
import copy,hashlib,importlib.util,json,sys,types
from pathlib import Path
HERE=Path(__file__).absolute().parent
POST=HERE/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'
def main():
    pkg='_T31_v5_OWNED_INERT_scope';parent=types.ModuleType(pkg);parent.__path__=[str(HERE/'pure')];sys.modules[pkg]=parent
    def load(leaf,path):
        name=pkg+'.'+leaf;spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
    load('protocol',HERE/'pure/protocol.py');load('handlers',HERE/'pure/handlers.py');C=load('workflow_output_contracts',POST/'workflow_output_contracts.py');M=load('workflow_output_material',POST/'workflow_output_material.py');S=load('workflow_output_scope',POST/'workflow_output_scope.py');checks=[]
    class OwnVault:
        def material(self,b):return originals[(b['ref'],b['sha256'])]
    class OwnChannel:
        def guard(self):return {'principal_ref':'OWNED-INERT:principal'}
        def policy_guard(self):return {'scope_refs':['OWNED-INERT:container']}
    original_cut={'store_ref':'OWNED-INERT:store','branch_ref':'OWNED-INERT:branch','commit_sequence':1,'commit_sha256':'a'*64,'source_profile_sha256':'b'*64,'streams':[]};host=types.SimpleNamespace(vault=OwnVault(),channel=OwnChannel(),handlers=types.SimpleNamespace(view=types.SimpleNamespace(owned_cut=original_cut)))
    native_path=(POST/'workflow_native_outputs.py').relative_to(S.ROOT).as_posix();gateway_path=(HERE/'pure/resolver_fixture.py').relative_to(S.ROOT).as_posix();pin=hashlib.sha256((S.ROOT/gateway_path).read_bytes()).hexdigest()
    control={'capability_binding':{'path':gateway_path,'sha256':pin},'capability_entrypoint':'NativeMixedPublisher.capture_selected'}
    selected={'schema_version':'lab-private-native-workflow-scope/v1-candidate','producer_binding':{'path':str(S.ROOT/gateway_path),'sha256':pin},'producer_entrypoint':control['capability_entrypoint'],'review_sha256':'1'*64,'source_binding':{'ref':'OWNED-INERT:source','sha256':'2'*64},'source_cut':original_cut,'principal_ref':'OWNED-INERT:principal','work_ref':'OWNED-INERT:work@1','container_scope_ref':'OWNED-INERT:container','authority_scope_ref':'OWNED-INERT:authority','permitted_body_scope_refs':['OWNED-INERT:body'],'authority_effect':'none'}
    def binding(ref,value):
        raw=C.json.dumps(value,sort_keys=True,separators=(',',':')).encode();b={'ref':ref,'sha256':C.sha(raw)};originals[(b['ref'],b['sha256'])]=raw;return b
    originals={};sb=binding('OWNED-INERT:scope',selected);cb=binding('OWNED-INERT:control',control);ref='transition:review-admission:applied'
    plan={'source_cut':original_cut,'principal_ref':'OWNED-INERT:principal','transitions':{ref:{'scope_contract_binding':sb,'producer_binding':{'path':native_path,'sha256':'3'*64},'producer_entrypoint':'NativeTypedResultAdapter.capture','producer_control_binding':cb,'output_scope_ref':'OWNED-INERT:container'}}}
    descriptor={'schema_version':'lab-private-late-workflow-inputs/v1-candidate','resolver_binding':{},'resolver_entrypoint':'LateInvocationInputs.resolve','assembler_binding':{},'assembler_entrypoint':'InvocationAssembler.bind','custody':{},'phase_contracts':{ref:{}}}
    host.workflow_invocation_inputs=M.LateInvocationInputs(host,{'invocation_inputs':descriptor,'transitions':{ref:{}}},guard=lambda:None,read_public=None,source_rows=set());host.workflow_invocation_inputs.active=host.vault
    scopes=S.ScopeContracts(host,plan);artifact={'scope_ref':'OWNED-INERT:container','identity_ref':'OWNED-INERT:record','version_ref':'OWNED-INERT:record@1','carrier_ref':'OWNED-INERT:carrier','byte_sha256':'4'*64}
    proof={k:copy.deepcopy(selected[k])for k in ['producer_binding','producer_entrypoint','review_sha256','source_binding','source_cut','principal_ref','work_ref','container_scope_ref','authority_scope_ref','authority_effect']};proof.update(schema_version='lab-original-native-record-scope/v1-candidate',artifact=artifact,body_scope_ref='OWNED-INERT:body')
    expected={'run_binding':{'ref':'OWNED-INERT:run','sha256':'6'*64},'work_ref':selected['work_ref'],'source_cut':original_cut,'principal_ref':selected['principal_ref']}
    assert scopes.validate(ref,artifact,'OWNED-INERT:body',proof,expected);checks.append('explicit selected native-only different container/body/authority axes join exact original proof')
    for field,bad in [('work_ref','OTHER'),('principal_ref','OTHER'),('review_sha256','5'*64),('source_cut',{'OTHER':True}),('body_scope_ref','OTHER'),('container_scope_ref','OTHER'),('authority_scope_ref','OTHER'),('producer_entrypoint','OTHER')]:
        altered=copy.deepcopy(proof);altered[field]=bad
        try:scopes.validate(ref,artifact,'OWNED-INERT:body',altered,expected)
        except ValueError:checks.append('scope proof refuses mismatched '+field)
        else:raise AssertionError(field)
    try:scopes.validate(ref,artifact,'OWNED-INERT:body',proof,dict(expected,work_ref='OWNED-INERT:Work-other@1'))
    except ValueError:checks.append('internally consistent native proof for B refuses expected capsule Work A')
    else:raise AssertionError('foreign expected Work')
    other=copy.deepcopy(plan);other['transitions'][ref]['producer_binding']['path']='OWNED-INERT:non-native.py'
    try:S.ScopeContracts(host,other)
    except ValueError:checks.append('scope differences do not waive ordinary producer body/header equality')
    else:raise AssertionError('ordinary producer scope waiver')
    return checks
