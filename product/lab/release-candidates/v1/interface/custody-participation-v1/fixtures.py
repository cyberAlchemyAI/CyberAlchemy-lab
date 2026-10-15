"""Private source/cut/host permission fixtures; no authentication or Agent claim."""
from dataclasses import replace
from datetime import datetime,timezone,timedelta
import copy
import json
import importlib.metadata
import platform
from pathlib import Path
import sys
from .eligibility import *

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
AUTH=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
AUTH_SHA='4d3c34a7f19b4b47892b3fbf5673544b36b0517e516961adcc77722f5d08e906'
KINDS={
    'principal':('principal/v1','record.json','node_id','principal:R03-source-fixture'),
    'project':('project-identity/v1','project.json','project_id','project:R03-source-fixture'),
    'product':('product-identity/v2','product.json','product_id','product:R03-source-fixture'),
    'goal':('goal/v1','goal.json','goal_id','goal:R03-source-fixture'),
    'intent':('intent/v1','record.json','node_id','intent:R03-source-fixture'),
    'work':('work/v1','record.json','node_id','work:R03-source-fixture'),
    'coordination-context':('coordination-context/v2','product-project-goal.json','coordination_context_id','coordination:R03-source-fixture'),
    'agent-assignment':('agent-assignment/v1','record.json','node_id','agent-assignment:R03-source-fixture'),
    'agent-profile':('agent-profile/v1','record.json','node_id','agent-profile:R03-source-fixture'),
    'agent-capability':('agent-capability/v1','record.json','node_id','agent-capability:R03-source-fixture'),
    'implementation':('implementation/v1','record.json','node_id','implementation:R03-source-fixture')}


class Fixture:
    def __init__(self,root,mutate=None,*,omit=(),postures=None,duplicate_identity=False):
        self.root=Path(root);require(self.root.is_dir() and self.root.is_relative_to(Path('/tmp')) and not any(self.root.iterdir()),'fresh private owned fixture root required')
        self.now=datetime.now(timezone.utc);self.bytes={};self.schemas=[];self.records=[];self.refs={};self.bodies={}
        for kind,(carrier,filename,identity_field,identity) in KINDS.items():
            base=ROOT/'authority/artifact-types'/carrier
            schema=(base/'schema.json').read_bytes()
            self.schemas.append(SchemaSpec('cal.artifact-type.'+carrier,kind,identity_field,schema,digest(schema)))
            body=json.loads((base/'fixtures/valid'/filename).read_bytes());body[identity_field]=identity
            self.bodies[kind]=body
        p=self.bodies['principal'];p['payload'].update(principal_kind='isolated-fixture-operator',stable_subject_ref='protocol:R03-synthetic-operator',registry_ref='protocol:R03-principal-registry',recognition_boundary_refs=['protocol:R03-local-recognition'])
        project=KINDS['project'][3];principal=KINDS['principal'][3];profile=KINDS['agent-profile'][3];goal=KINDS['goal'][3]
        implementation=KINDS['implementation'][3]+'@fixture.1';cap=KINDS['agent-capability'][3]
        self.bodies['work']['payload'].update(project_ref=project,goal_refs=[goal],input_refs=[KINDS['intent'][3]],output_refs=['protocol:R03-expected-output'],completion_state='candidate-prepared')
        self.bodies['agent-assignment']['payload'].update(eligible_agent_ref=profile,owner_ref=principal,project_ref=project,work_ref=KINDS['work'][3],intent_ref=KINDS['intent'][3],period='protocol:R03-assignment-period',expected_output_refs=['protocol:R03-expected-output'])
        self.bodies['work']['relation_refs']=[{'relation_kind_ref':'relation.member-of','direction':'source','counterpart_kind':'project','counterpart_ref':project}]
        self.bodies['agent-assignment']['relation_refs']=[{'relation_kind_ref':'relation.member-of','direction':'source','counterpart_kind':'project','counterpart_ref':project},{'relation_kind_ref':'relation.addresses-intent','direction':'source','counterpart_kind':'intent','counterpart_ref':KINDS['intent'][3]}]
        self.bodies['agent-capability']['relation_refs']=[{'relation_kind_ref':'relation.has-capability','direction':'target','counterpart_kind':'agent-profile','counterpart_ref':profile}]
        self.bodies['agent-profile']['payload'].update(policy_refs=['protocol:R03-source-policy'],allowed_input_kinds=['context-view','ontology-view'])
        self.bodies['agent-profile']['relation_refs']=[{'relation_kind_ref':'relation.has-capability','direction':'source','counterpart_kind':'agent-capability','counterpart_ref':cap}]
        self.bodies['implementation']['payload'].update(execution_entrypoint_ref='protocol:R03-fixture-reader-entrypoint',environment_contract_ref='protocol:R03-selected-environment')
        self.bodies['agent-capability']['payload'].update(implementation_refs=[implementation],input_contract_refs=['protocol:R03-input-contract'],output_contract_refs=['protocol:R03-output-contract'],evidence_contract_refs=['protocol:R03-evidence-contract'],failure_mode_refs=['protocol:R03-failure-boundary'])
        self.bodies['coordination-context'].update(project_ref=project,product_ref=KINDS['product'][3],goal_ref=goal,source_policy_refs=['protocol:R03-source-policy'],consumer_refs=[profile],intended_uses=['read-verified-context'],bounded_context_refs=[])
        if mutate:mutate(self.bodies)
        for kind,body in self.bodies.items():
            if kind in omit:continue
            carrier,_,identity_field,identity=KINDS[kind]
            raw=(json.dumps(body,indent=3,ensure_ascii=False)+'\n').encode();path=self.root/(kind+'.json');path.write_bytes(raw);path.chmod(0o600)
            self.bytes[path]=raw
            ref={'scope_ref':project,'identity_ref':body[identity_field],'version_ref':body[identity_field]+'@'+body.get('version','fixture.1'),'carrier_ref':'cal.artifact-type.'+carrier,'byte_sha256':digest(raw)}
            self.refs[kind]=ref
            self.records.append(SourceRecord(ref,raw,(postures or {}).get(kind,'isolated-candidate-current'),path.name))
        if duplicate_identity:
            original=next(r for r in self.records if r.artifact['identity_ref']==goal)
            self.records.append(SourceRecord({**original.artifact,'version_ref':goal+'@another'},original.original,original.posture,'goal-another-original'))
        self.cut={'store_ref':'store:R03-preflight-fixture','branch_ref':'branch:R03-preflight-fixture',
            'source_profile_sha256':digest(json.dumps({p.name:digest(raw) for p,raw in self.bytes.items()},sort_keys=True).encode()),'commit_sequence':0,'commit_sha256':'0'*64,
            'streams':[{'stream_ref':'semantic:R03-fixture','cursor':0,'head_sha256':'0'*64},
            {'stream_ref':'governance:R03-fixture','cursor':0,'head_sha256':'0'*64}]}
        self.sources=ExactSources(project,self.cut,self.records,self.schemas,self.guard)
        evidence={'ref':AUTH.relative_to(ROOT).as_posix(),'sha256':AUTH_SHA}
        protocols={}
        for ref,kind in [
            ('protocol:R03-source-policy','policy'),('protocol:R03-input-contract','input-contract'),
            ('protocol:R03-output-contract','output-contract'),('protocol:R03-evidence-contract','evidence-contract'),
            ('protocol:R03-failure-boundary','failure-boundary')]:
            value={'schema_version':'lab-isolated-protocol-declaration/v1-candidate','reference':ref,'kind':kind,'reference_class':'protocol-reference',
                'statement':'Isolated source/permission preflight fixture; no runtime implementation, admission or action is proved.','authority_effect':'none','actual_owner_outcome':None}
            raw=(json.dumps(value,indent=2)+'\n').encode();path=self.root/('protocol-'+kind+'.json');path.write_bytes(raw);path.chmod(0o600);self.bytes[path]=raw
            protocols[ref]={'kind':kind,'binding':{'ref':path.name,'sha256':digest(raw)}}
        impl_evidence={'schema_version':'lab-isolated-implementation-binding/v1-candidate','implementation_version_ref':implementation,
            'entrypoint_ref':'protocol:R03-fixture-reader-entrypoint','environment_contract_ref':'protocol:R03-selected-environment',
            'code_binding':{'ref':str(HERE/'eligibility.py'),'sha256':digest((HERE/'eligibility.py').read_bytes())},
            'environment':{'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema')},
            'claim_ceiling':'Selected preflight test module only. This is not a complete Machine Agent implementation or conformance result.','authority_effect':'none','actual_owner_outcome':None}
        raw=(json.dumps(impl_evidence,indent=2)+'\n').encode();path=self.root/'implementation-selection.json';path.write_bytes(raw);path.chmod(0o600);self.bytes[path]=raw
        implementation_binding={'ref':path.name,'sha256':digest(raw)}
        self.permission=SessionPermission(principal,project,frozenset(['context.get','session.open']),
            (self.now-timedelta(minutes=1)).isoformat(),(self.now+timedelta(minutes=20)).isoformat(),
            {'protocol:R03-assignment-period':[(self.now-timedelta(minutes=1)).isoformat(),(self.now+timedelta(minutes=10)).isoformat()]},
            frozenset(['protocol:R03-source-policy']),frozenset(),frozenset(),(evidence,),64,65536,1048576,900,
            {implementation:{'entrypoint_ref':'protocol:R03-fixture-reader-entrypoint','environment_contract_ref':'protocol:R03-selected-environment','evidence_binding':implementation_binding}},protocols)
        self.actor={'principal_ref':principal,'role_assignment_refs':[],'agent_instance_ref':None,'session_ref':None,'assignment_ref':None}
        self.authority=SessionEligibility(self.sources,lambda:self.permission,self.permission_guard,clock=lambda:self.now)
        self.delivery_binding={'ref':'protocol:R03-delivery-fixture','sha256':'1'*64}
        self.envelope_binding={'ref':'protocol:R03-authority-envelope-fixture','sha256':'2'*64}
        self.delivery={'verified_original_binding':self.delivery_binding,'posture':'ready','scope_enforced':True,'freshness':'current','source_cut':copy.deepcopy(self.cut),
            'assignment':self.refs.get('agent-assignment'),'authenticated_principal_ref':principal,'authority_envelope_binding':self.envelope_binding,
            'work':self.refs.get('work'),'coordination_context':self.refs.get('coordination-context'),'expires_at':(self.now+timedelta(minutes=5)).isoformat()}

    def guard(self):
        return all(p.is_file() and not p.is_symlink() and p.read_bytes()==raw and p.stat().st_mode & 0o777==0o600 for p,raw in self.bytes.items())

    def permission_guard(self,permission):
        # Current explicit construction instruction; not admission or a human role.
        valid=AUTH.is_file() and digest(AUTH.read_bytes())==AUTH_SHA and permission.evidence_bindings==self.permission.evidence_bindings
        for selected in permission.protocol_bindings.values():
            b=selected['binding'];path=self.root/b['ref'];valid=valid and path.is_file() and digest(path.read_bytes())==b['sha256'] and json.loads(path.read_bytes())['kind']==selected['kind']
        for selected in permission.implementation_bindings.values():
            b=selected['evidence_binding'];path=self.root/b['ref'];valid=valid and path.is_file() and digest(path.read_bytes())==b['sha256']
            if path.is_file():
                value=json.loads(path.read_bytes());code=Path(value['code_binding']['ref']);valid=valid and code.is_file() and digest(code.read_bytes())==value['code_binding']['sha256'] and value['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema')}
        return valid

    def budget(self,actions):
        return {'max_actions':actions,'max_input_bytes':65536,'max_output_bytes':1048576,'deadline':(self.now+timedelta(minutes=8)).isoformat()}

    def context(self):
        return {'schema_version':'lab-context-query/v1-candidate','request_ref':'request:R03-context-preflight',
            'actor':copy.deepcopy(self.actor),'assignment':self.refs['agent-assignment'],'work':self.refs['work'],'coordination_context':self.refs['coordination-context'],
            'source_cut':copy.deepcopy(self.cut),'intended_use':'read-verified-context','selectors':[],'exclusions':[],
            'freshness_requirement':'current','budget':self.budget(0),'authority_effect':'none'}

    def open(self):
        return {'schema_version':'lab-agent-session-open/v1-candidate','request_ref':'request:R03-session-preflight','actor':copy.deepcopy(self.actor),
            'assignment':self.refs['agent-assignment'],'profile':self.refs['agent-profile'],'implementation':self.refs['implementation'],
            'capabilities':[self.refs['agent-capability']],'context_delivery_binding':copy.deepcopy(self.delivery_binding),'authority_envelope_binding':copy.deepcopy(self.envelope_binding),
            'source_cut':copy.deepcopy(self.cut),'budget':self.budget(1),'memory_policy':{'persistence_allowed':False,'expires_with_session':True},'authority_effect':'none'}

    def context_plan(self):return self.authority.context_plan(self.context(),self.actor,self.refs['agent-profile'])
    def open_plan(self,**changes):
        message=self.open();message.update(changes)
        return self.authority.open_plan(message,self.actor,lambda _:copy.deepcopy(self.delivery))
