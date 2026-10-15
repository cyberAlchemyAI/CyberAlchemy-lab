"""Closed independent routing; public input supplies no challenger grant."""
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v60'
def obj(properties):return {'type':'object','additionalProperties':False,'properties':properties,'required':list(properties)}
def main():
    common='urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/'
    binding={'$ref':common+'binding'};artifact={'$ref':common+'artifact_ref'};text={'type':'string','minLength':1}
    receipt=obj({'path':text,'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}})
    evidence=obj({'kind':{'enum':['source','evidence-set','decision','validation-receipt']},'binding':binding,
        'artifact':{'anyOf':[artifact,{'type':'null'}]},'receipt_binding':{'anyOf':[receipt,{'type':'null'}]}})
    properties={'schema_version':{'const':'lab-independent-challenge-submit-routing/v1-candidate'},
        'principal_ref':text,'storage_scope_ref':text,'candidate_scope_ref':text,
        'challenge_contract':artifact,'challenger':artifact,'source_cut':{'$ref':common+'source_cut'},
        'subjects':{'type':'array','minItems':1,'maxItems':64,'uniqueItems':True,'items':artifact},
        'grounds':{'type':'array','minItems':1,'maxItems':64,'uniqueItems':True,'items':text},
        'accepted_evidence':{'type':'array','minItems':1,'maxItems':128,'uniqueItems':True,'items':evidence},
        'policy_ref':text,'owner_route':text,'resolution_gate_ref':text,'residue_route_ref':text,'response_mode':text,
        'not_before':{'type':'string','format':'date-time'},'expires_at':{'type':'string','format':'date-time'},
        'revoked':{'const':False},'development_authorization_binding':binding,
        'actual_owner_outcome':{'type':'null'},'authority_effect':{'const':'none'}}
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema',
        '$id':'urn:cyberalchemy-lab:independent-challenge-submit-routing:v1-candidate',**obj(properties)}
    with (API/'challenge-routing.schema.json').open('x') as stream:json.dump(schema,stream,indent=2,sort_keys=True);stream.write('\n')
    print('Authored closed challenger routing schema with original public common references.',flush=True)
if __name__=='__main__':main()
