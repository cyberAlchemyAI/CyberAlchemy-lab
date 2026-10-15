"""Materialize closed private composition controls in an immutable successor."""
import ast,copy,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-v71';API=BASE/'api-v72'
def replace(p,a,b):
    s=p.read_text();assert s.count(a)==1,(p,a);p.write_text(s.replace(a,b,1))
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v22').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore);shutil.copytree(BASE/'lesson-host-composition-v21',BASE/'lesson-host-composition-v22',ignore=ignore)
    replace(BASE/'lesson-host-composition-v22/host.py','api-v71/service.py','api-v72/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v21','lesson-host-composition-v22')
    shutil.copyfile(RUN/'API72-workflow_composition.py',API/'workflow_composition.py')
    kind='lab-local-challenge-review-policy/v1-candidate'
    binding={'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}
    digest={'type':'string','pattern':'^[0-9a-f]{64}$'}
    producer={'type':'object','additionalProperties':False,'properties':{'source':{'const':'completed-producer'},'operation':{'const':'challenge.submit'},'idempotency_key':{'type':'string','minLength':1},'target_version_ref':{'type':'string','minLength':1},'byte_sha256':digest,'core_sha256':digest},'required':['source','operation','idempotency_key','target_version_ref','byte_sha256','core_sha256']}
    provisioned={'type':'object','additionalProperties':False,'properties':{'source':{'const':'provisioned-input'},'target_binding':binding},'required':['source','target_binding']}
    properties={'schema_version':{'const':'lab-independent-workflow-composition/v1-candidate'},'principal_ref':{'type':'string','minLength':1},'scope_ref':{'type':'string','minLength':1},'authorization_basis_binding':binding,'base_cut_binding':binding,'not_before':{'type':'string','format':'date-time'},'expires_at':{'type':'string','format':'date-time'},'revoked':{'const':False},'proposal_ref':{'type':'string','minLength':1},'idempotency_key':{'type':'string','minLength':1},'members':{'type':'array','minItems':1,'maxItems':64,'items':{'oneOf':[producer,provisioned]}},'authority_effect':{'const':'none'},'actual_owner_outcome':{'type':'null'}}
    emit(API/'workflow-composition.schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:cyberalchemy-lab:private-workflow-composition:v1-candidate','type':'object','additionalProperties':False,'properties':properties,'required':list(properties)})
    p=API/'protocol.py';replace(p,"CHALLENGE_SUPPORTED=METADATA_SUPPORTED+('challenge.submit',)","CHALLENGE_SUPPORTED=METADATA_SUPPORTED+('challenge.submit',)\nWORKFLOW_SUPPORTED=CHALLENGE_SUPPORTED+('proposal.review',)")
    p=API/'auth.py'
    replace(p,"        challenge=value['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'", "        workflow=value['schema_version']=='lab-local-challenge-review-policy/v1-candidate'\n        challenge=workflow or value['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'")
    replace(p,"        if challenge:fields+=['challenge_control']", "        if challenge:fields+=['challenge_control']\n        if workflow:fields+=['composition_control']")
    replace(p,"'lab-local-challenge-candidate-policy/v1-candidate')", "'lab-local-challenge-candidate-policy/v1-candidate','lab-local-challenge-review-policy/v1-candidate')")
    replace(p,"list(PACKAGE_EXPORT_SUPPORTED if package_export", "list(WORKFLOW_SUPPORTED if workflow else PACKAGE_EXPORT_SUPPORTED if package_export")
    replace(p,"        if package_export:\n            from .package_export import validate_control", "        if workflow:\n            from .workflow_composition import validate_control as validate_composition\n            source.require(value['scope_control'] is None,'workflow composition cannot add an undeclared domain-scope policy')\n            validate_composition(value,self.schemas)\n        if package_export:\n            from .package_export import validate_control")
    replace(p,"('durable-metadata-and-exact-package-export' if package_export", "('durable-metadata-and-exact-challenge-review-composition' if workflow else 'durable-metadata-and-exact-package-export' if package_export")
    p=API/'authentication.schema.json';schema=json.loads(p.read_bytes())
    challenge=next(branch for branch in schema['oneOf'] if branch.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-challenge-candidate-policy/v1-candidate')
    branch=copy.deepcopy(challenge);branch['properties']['schema_version']={'const':kind};branch['properties']['purpose']={'const':'durable-metadata-and-exact-challenge-review-composition'}
    ops=branch['properties']['allowed_operations'];assert ops['const'][-1]=='challenge.submit';ops['const'].append('proposal.review')
    branch['properties']['composition_control']={'type':'object','additionalProperties':False,'properties':{'selection_binding':binding},'required':['selection_binding']};branch['required'].append('composition_control');branch['properties']['scope_control']={'type':'null'}
    schema['oneOf'].append(branch);p.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    p=API/'challenge_submission.py';replace(p,"policy['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'", "policy['schema_version'] in ('lab-local-challenge-candidate-policy/v1-candidate','lab-local-challenge-review-policy/v1-candidate')")
    p=API/'generated_candidate.py'
    replace(p,"        require(self.selected.get(b['ref'])==b,'material not selected by exact reconstructed completed producer')", "        if b['ref'] in self.inputs:\n            return self.vault.material(b)\n        require(self.selected.get(b['ref'])==b,'material not selected by exact reconstructed completed producer')")
    replace(p,"require(policy['schema_version']=='lab-local-challenge-candidate-policy/v1-candidate'", "require(policy['schema_version'] in ('lab-local-challenge-candidate-policy/v1-candidate','lab-local-challenge-review-policy/v1-candidate')")
    p=API/'service.py';replace(p,'from .generated_candidate import GeneratedCandidateHandlers','from .generated_candidate import GeneratedCandidateHandlers\nfrom .workflow_composition import WorkflowCandidateHandlers')
    replace(p,'self.candidates=GeneratedCandidateHandlers(self)','self.candidates=WorkflowCandidateHandlers(self)')
    replace(p,"'generated_candidate.py')","'generated_candidate.py','workflow_composition.py','workflow-composition.schema.json')")
    p=API/'review_preparation.py';replace(p,'self.schemas=service.schemas;self.vault=service.vault','self.schemas=service.schemas;self.vault=service.vault;self.materials=self.vault')
    replace(p,"        profile,preference=self.resolve_routing(proposal)","        if self.service.candidates.needed(proposal):\n            from .guarded_candidate import selection\n            with selection(self.service):self.materials=self.service.candidates.selected(proposal,message['source_cut'])\n        profile,preference=self.resolve_routing(proposal)")
    text=p.read_text();assert text.count('self.vault.material(')==3;text=text.replace('self.vault.material(','self.materials.material(');p.write_text(text)
    for p in API.rglob('*.py'):ast.parse(p.read_bytes())
    print(json.dumps({'result':'AUTHORED','successor':'api-v72','original_public_contracts':34,'authored_handlers':21,'missing_operations':13,'new_private_policy':kind,'runtime_qualified':False,'authority_effect':'none'}))
if __name__=='__main__':main()
