"""Exact per-member scope planning. Metadata never creates a grant or body copy."""
from dataclasses import dataclass,asdict
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[6]
SOURCE=ROOT/'product/lab/release-candidates/v1/release-validation/0001/final-materializer-selection-0276.json'
BASE=ROOT/'product/lab/release-candidates/v1/release-validation/0001/base-state-registry-history-0276.json'
PROFILE=ROOT/'product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/write-profile.json'
CONSUMER=ROOT/'product/lab/release-candidates/v1/interface/custody-correction-v4/runtime/lab_runtime/operations.py'
PROJECT='project:cyberalchemy-v2-to-lab-migration'
DOMAIN_COUNTS={'lab.legacy-source-assertion.cav2-product-thesis':220,'scope:lab-runtime-local:w06-learning-0002-560605b8':6,'scope:lab-integrated-model':1,'project:cyberalchemy-v2-to-lab-migration@foundation.1':1,'protocol:lab-final-review:C10':1,'scope:lab-runtime-local:o02-source-withdrawal-fixture':1}
PRODUCERS={
 'implementation/lab-review/candidates/v1/packages/0001/preparation.json':'implementation/lab-review/candidates/v1/prepare.py',
 'implementation/lab-workflows/candidates/v1/review/W08/packages/0001/preparation.json':'implementation/lab-workflows/candidates/v1/review/W08/packet.py',
 'implementation/lab-ontology/candidates/v1/review/O06/packages/0001/preparation.json':'implementation/lab-ontology/candidates/v1/review/O06/package.py',
}

def require(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(raw):
    def pairs(rows):
        result={}
        for k,v in rows:require(k not in result,'duplicate metadata field');result[k]=v
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite metadata')))
def original(binding):
    require(set(binding)=={'path','sha256'},'closed original metadata binding required')
    p=ROOT/binding['path'];require(p.is_relative_to(ROOT) and '..' not in p.parts and not any(x.is_symlink() for x in [p,*p.parents]),'metadata path outside repository')
    raw=p.read_bytes();require(sha(raw)==binding['sha256'],'original metadata bytes changed');return raw
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}

@dataclass(frozen=True)
class MemberRoute:
    member_ref:str
    selection_index:int
    selected_axes_sha256:str
    body_binding:dict
    body_scope_ref:str
    carrier_ref:str
    schema_binding:dict
    descriptor_binding:dict
    category:str
    operation:str
    version_ref:str
    decision_ref:str
    producer_preparation_binding:dict
    review_packaging_code_binding:dict
    original_body_origin_bindings:tuple
    historical_producer_execution_proven:bool
    consumer_code_binding:dict
    visibility:str
    owner_roles_required:tuple
    correction_eligibility:dict

class ScopeRouter:
    def __init__(self,selection_binding,base_binding,profile_binding):
        require(selection_binding['path']==SOURCE.relative_to(ROOT).as_posix() and base_binding['path']==BASE.relative_to(ROOT).as_posix() and profile_binding=={'path':PROFILE.relative_to(ROOT).as_posix(),'sha256':'00609ef4c881546c0f63bec905c3f03422ea42dd2e2154e3dc152141537822fd'},'independent selected metadata locations differ')
        self.selection_binding=selection_binding;self.base_binding=base_binding;self.profile_binding=profile_binding
        self.selection=parse(original(selection_binding));self.base=parse(original(base_binding));self.profile=parse(original(profile_binding));self.rows=[]
        require(self.selection['original_member_count']==363 and len(self.selection['members'])==363 and self.selection['authority_effect']=='none' and self.selection['actual_owner_outcome'] is None,'original complete candidate selection required')
        self.config=self.base['original_config'];require(self.config['scope_ref']==PROJECT and self.config['authorized_domain_scope_refs']==self.profile['authorized_domain_scope_refs']==['scope:cyberalchemy-lab-first-agent-episode'],'original Project/correction grant changed')
        preparations={}
        for index,member in enumerate(self.selection['members']):
            axes=member['axes'];domain=axes.get('original_body_scope_ref')
            if domain in [None,PROJECT]:continue
            preparation=member['original_preparation_binding'];p=preparation['path']
            require(p in PRODUCERS,'unknown original producer')
            if p not in preparations:preparations[p]=parse(original(preparation))
            package=preparations[p];found=[m for m in package['members'] if m.get('member_ref',m.get('member_id'))==member['member_ref']];require(len(found)==1,'original producer member missing/ambiguous');producer=found[0]
            visibility='private-source-qualified-metadata' if member['member_class']=='metadata-carrier-admission' else 'candidate-repository-reference-only'
            if visibility.startswith('private'):
                scope=producer['scope'];require(scope['visibility']==visibility and scope['source_scope_ref']==domain and producer['postimage_binding']==axes['body_binding'],'private producer scope/postimage differs')
            eligibility={'eligible':False,'reasons':[],'profile_binding':profile_binding,'current_domain_grant_status':'historical-fixture-selection-only'}
            if domain not in self.profile['authorized_domain_scope_refs']:eligibility['reasons'].append('domain outside original reviewed correction profile')
            if axes['category']!=self.profile['permitted_category'] or axes['operation']!=self.profile['permitted_operation']:eligibility['reasons'].append('exact original correction permits typed-relation revise only')
            eligibility['eligible']=not eligibility['reasons']
            require(not eligibility['eligible'],'this routing candidate must not silently activate a new correction route')
            require(axes['original_body_scope_changed'] is False and axes['owner_authority_resolved'] is False and axes['body_binding']['sha256']==axes['body_byte_sha256'],'original body/owner posture differs')
            row=MemberRoute(member['member_ref'],index,sha(json.dumps(axes,sort_keys=True,separators=(',',':')).encode()),axes['body_binding'],domain,axes['carrier_ref'],axes['schema_binding'],axes['descriptor_binding'],axes['category'],axes['operation'],axes['version_ref'],axes['decision_ref'],preparation,bind(ROOT/PRODUCERS[p]),tuple(member['original_target_bindings']),False,bind(CONSUMER),visibility,tuple(member['proposed_owner_roles']),eligibility)
            self.rows.append(row)
        require(len(self.rows)==230 and len({r.member_ref for r in self.rows})==230 and len({r.body_binding['path'] for r in self.rows})==230,'all230 exact original bodies required')
        counts={d:sum(r.body_scope_ref==d for r in self.rows) for d in DOMAIN_COUNTS};require(counts==DOMAIN_COUNTS,'original domain grouping differs')
        self.routes={r.member_ref:r for r in self.rows};self.guard()
    def guard(self):
        original(self.selection_binding);original(self.base_binding);original(self.profile_binding)
        for row in self.rows:
            axes=self.selection['members'][row.selection_index]['axes'];require(sha(json.dumps(axes,sort_keys=True,separators=(',',':')).encode())==row.selected_axes_sha256,'route original axes changed')
            original(row.producer_preparation_binding);original(row.review_packaging_code_binding);original(row.consumer_code_binding)
    def select(self,member_ref,domain_scope_ref,body_sha256,*,destination_visibility='private-reference-only'):
        require(member_ref in self.routes,'unknown member route');row=self.routes[member_ref]
        require(domain_scope_ref==row.body_scope_ref,'body domain cannot be flattened or aliased')
        require(body_sha256==row.body_binding['sha256'],'original body digest differs')
        require(destination_visibility=='private-reference-only','original private/source bodies cannot be publicly exported')
        return row
    def plan(self):
        self.guard();groups=[]
        for domain,count in DOMAIN_COUNTS.items():
            rows=[r for r in self.rows if r.body_scope_ref==domain]
            groups.append({'domain_scope_ref':domain,'member_refs':[r.member_ref for r in rows],'member_count':count,'route_kind':'exact-domain-consumer-candidate','consumer_code_binding':bind(CONSUMER),'Project_grant_expanded':False,'actual_current_domain_grant':None,'governing_owner_assignments':None,'owner_gate':'independent domain owner assignment/scope/period and exact S02/R08 member response; original fixture roles do not establish governing authority','body_delivery':'reference-only; private consumer access required before actual byte/schema/current-cut verification'})
        return {'schema_version':'lab-exact-body-scope-routes/v1-candidate','selection_binding':self.selection_binding,'base_binding':self.base_binding,'profile_binding':self.profile_binding,'original_member_count':363,'all230_original_scope_bodies_accounted':True,'routes':[parse(json.dumps(asdict(r))) for r in self.rows],'groups':groups,'current_status':'BLOCKED-ON-DOMAIN-PROVISIONING-AND-OWNER-ACCESS','actual_successful_operational_routes':0,'original_bodies_read':0,'private_body_exports':0,'noBodyCopyPrivate':True,'Project_grant_expanded':False,'body_scopes_rewritten':False,'source_body_currentness':'not-reverified; exact historical selected bindings only','private_or_live_state_mutated':False,'role_assignments_created':0,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    def validate_plan(self,plan):
        require(plan==self.plan(),'route plan differs from complete independently selected original member/scope/privacy/grant closure')
        return {'result':'PASS-CANDIDATE-METADATA','members':230,'operational_routes_authorized':0,'actual_owner_outcome':None,'authority_effect':'none'}
    def operational_preflight(self,route):
        require(type(route) is MemberRoute and route==self.routes.get(route.member_ref),'exact independently selected route required')
        raise ValueError('No independently provisioned current consumer/domain grant, protected body access or governing owner response is supplied by this candidate')
    def export_original_body(self,route):
        raise ValueError('Original private/source body export is excluded; route references confer no body access')
