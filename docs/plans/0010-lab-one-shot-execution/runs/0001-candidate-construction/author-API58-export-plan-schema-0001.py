"""Materialize the closed independently selected export-plan schema."""
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v58'
COMMON='urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/'
def ref(name):return {'$ref':COMMON+name}
def closed(properties):return {'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
def main():
    properties={
        'schema_version':{'const':'lab-package-export-plan/v1-candidate'},
        'source_cut':ref('source_cut'),'export_contract_binding':ref('binding'),
        'privacy_review_binding':ref('binding'),
        'source_proposal_binding':{'anyOf':[ref('binding'),{'type':'null'}]},
        'materials':{'type':'array','minItems':1,'maxItems':1000,'items':closed({
            'binding':ref('binding'),'artifact':{'anyOf':[ref('artifact_ref'),{'type':'null'}]},
            'dependencies':{'type':'array','maxItems':1000,'items':ref('binding')},
            'origin':{'enum':['artifact','schema','source-proof','proposal-input']},
            'encoding':{'const':'json-utf8'}})},
        'output_root':{'type':'string','minLength':1},
        'output_root_scope_ref':{'type':'string','minLength':1},
        'output_root_identity':closed({'device':{'type':'integer','minimum':0},'inode':{'type':'integer','minimum':1}}),
        'scope_binding':ref('binding'),'max_package_bytes':{'type':'integer','minimum':1,'maximum':67108864},
        'max_generations':{'type':'integer','minimum':1,'maximum':64},
        'authority_effect':{'const':'none'},'actual_owner_outcome':{'type':'null'}}
    value={'$id':'urn:cyberalchemy-lab:internal:package-export-plan:v1-candidate',
        '$schema':'https://json-schema.org/draft/2020-12/schema',**closed(properties)}
    path=API/'schemas/package-export-plan.schema.json'
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    print('Materialized closed independently selected package export plan schema.',flush=True)

if __name__=='__main__':main()
