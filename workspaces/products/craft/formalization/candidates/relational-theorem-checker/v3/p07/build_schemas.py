"""Closed owned-run/phase/owner and normalized execution state contracts."""
from pathlib import Path
import copy
import json
HERE=Path(__file__).resolve().parent
def obj(props,required=None):return {'type':'object','properties':props,'required':list(props) if required is None else required,'additionalProperties':False}
def arr(items):return {'type':'array','items':items}
def nullable(v):return {'oneOf':[v,{'type':'null'}]}
text={'type':'string','minLength':1};digest={'type':'string','pattern':'^[0-9a-f]{64}$'}
ref=obj({'path':{'type':'string','pattern':r'^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[^\\]+$'},'sha256':digest})
base={'authority_effect':{'const':'none'}}
owner=obj({'schema':{'const':'relational.run-owner/v3'},'run_id':text,'ownership_token':{'type':'string','pattern':'^[0-9a-f]{32}$'},'job':text,'cleanup':{'const':'proposal-only; accepted and other runs excluded'},**base})
cache=obj({'schema':{'const':'relational.cache-check/v3'},'cache_key':digest,'anchor':ref,'checked':arr(ref),'fresh_qualification':{'const':False},**base})
phase=obj({'schema':{'const':'relational.run-phase/v3'},'run_id':text,'index':{'type':'integer','minimum':0},'name':text,'owner':ref,'previous':nullable(ref),'request_bytes_sha256':digest,'request_identity':nullable(digest),'policy_identity':digest,'inputs':arr(ref),'outputs':arr(ref),'cache_check':nullable(cache),'fresh_qualification':{'const':False},**base})
record=obj({'schema':{'const':'relational.owned-run-record/v3'},'run_id':text,
            'phase':{'enum':['prepared','completed','invalid','unsupported','unknown-resource','cancelled','unsupported-policy']},
            'request_identity':nullable(digest),'request_bytes_sha256':digest,'policy_identity':digest,'owner':nullable(ref),
            'inputs':arr(ref),'outputs':arr(ref),'phases':arr(ref),'cache_check':nullable(cache),
            'resource_events':arr(obj({'kind':text,'detail':{'type':'string'}})),
            'timings':obj({'supervised_seconds':{'type':'number','minimum':0}},[]),'result':nullable(ref),
            'application_authorized':{'const':False},**base})
record['allOf']=[{'if':{'properties':{'phase':{'const':'completed'}}},'then':{'properties':{'result':ref,'owner':ref,'request_identity':digest,'cache_check':cache}}}]
ids=arr({'type':'string','pattern':r'^(P(?:0[0-9]|1[01])|E0[0-6])$'});ids['uniqueItems']=True
state=obj({'schema':{'const':'relational.execution-state/v3'},'accepted':ids,'remaining_required':ids,'remaining_optional':ids,
           'resolved_optional':arr(obj({'id':{'type':'string','pattern':'^E0[0-6]$'},'resolution':{'const':'not-needed'}})),
           'complete':{'type':'boolean'},**base})
for name,schema in [('owner',owner),('phase',phase),('run-record',record),('execution-state',state)]:
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:owned-'+name,**schema}
    (HERE/(name+'.schema.json')).write_text(json.dumps(schema,indent=2)+'\n')
envelope=copy.deepcopy(json.loads((HERE.parent/'p06/supervised-result.schema.json').read_text()))
envelope['$id']='urn:relational:v3:owned-qualification-result'
for variant in envelope['oneOf']:
    variant['properties']['schema']={'const':'relational.owned-qualification/v3'}
    variant['properties']['owned_run']=ref
    variant['properties']['seconds_including_owned_finalization']={'type':'number','minimum':0}
    variant['required'].append('seconds_including_owned_finalization')
    if variant['properties']['status']=={'const':'qualified-candidate'}:variant['required'].append('owned_run')
(HERE/'result.schema.json').write_text(json.dumps(envelope,indent=2)+'\n')
