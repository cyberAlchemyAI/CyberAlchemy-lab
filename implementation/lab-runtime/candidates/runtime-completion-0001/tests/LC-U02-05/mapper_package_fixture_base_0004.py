"""Owned synthetic dependency for the unchanged full historical projection.
No signatures, protected reads, current host authority or native validations.
"""
from pathlib import Path
from types import SimpleNamespace as N
import hashlib
import json

HERE=Path(FIXTURE_CONFIG['mapped']);ROOT=Path(FIXTURE_CONFIG['root'])
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def require(ok,code):
    if not ok:raise ValueError('SYNTHETIC_DEPENDENCY_REFUSAL')
def load(path):return json.loads(path.read_bytes())
def binding(path):return {'path':str(path),'sha256':sha(path.read_bytes())}
def original(b):
    p=Path(b['path']);require(p.is_relative_to(ROOT),'FIXTURE_BOUND');v=p.read_bytes();require(sha(v)==b['sha256'],'FIXTURE_SHA');return v
def verify_source(pin):require(pin==sha((HERE/'source-manifest.json').read_bytes()),'FIXTURE_SOURCE')
attrs=['PRINCIPAL','PRINCIPAL_REFERENCE','GOAL','WORK','INTENT','PROFILE','ASSIGNMENT','COORDINATION','CONTEXT','CAPABILITY','IMPLEMENTATION']
records=N(**{name:'fixture:'+name.lower() for name in attrs},PRODUCT_CAPABILITY='fixture:product-capability',PREFIX='fixture',VERSION='1')
ids=[getattr(records,n) for n in attrs]+['fixture:scope','product:cyberalchemy-lab','fixture:project','fixture:product-capability']
rows=FIXTURE_CONFIG['subjects'];subjects={r['version_ref']:r for r in rows}
contract={'semantic_definition_refs':['definition:fixture@1'],'semantic_kind':'fixture-kind','schema_sha256':'1'*64,'schema_path':'fixture-schema'}
proj={'state':{'node_id':'fixture:project'},'contracts':{name:dict(contract) for name in ('fixture.node/v1','cal.artifact-type.ontology-node/v2','cal.artifact-type.typed-relation/v3')},'subjects':{'definition:fixture@1':FIXTURE_CONFIG['definition']}}
def record_bytes(view,s):
    b=s['source'];raw=original(b);return raw,b['path'],'original-file-bytes',b['sha256']
def artifact_ref(view,s):
    raw,_,_,_=record_bytes(view,s)
    return {'identity_ref':s['identity'],'version_ref':s['version_ref'],'carrier_ref':s['carrier_ref'],'byte_sha256':sha(raw)}
def validate_record(record,carrier,projection):require(type(record)is dict and carrier in projection['contracts'],'FIXTURE_RECORD')
def validate_relation(record,projection):require(type(record.get('payload'))is dict,'FIXTURE_RELATION')
view=N(subjects=subjects,data={'projection':proj},handle=N(operations=N(validate_record=validate_record,validate_relation=validate_relation),mapping=N(subject_kind=lambda s,p:'fixture-kind')))
class Source:
    view=view;sources=N(scope_ref='fixture:scope');source_cut={'fixture_only':True,'sha256':'2'*64};selected={'name':'fixture-source'}
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def guard(self):verify_source(FIXTURE_CONFIG['mapper_pin'])
    def closure_report(self):return {'fixture_only':True,'subjects':25}
def open_signed(source,package):
    require(source==FIXTURE_CONFIG['source_pin'] and package==FIXTURE_CONFIG['reader_pin'],'FIXTURE_READER_PINS');return Source()
def signature(view,kind):return {'payload':{'axis_id':'fixture-axis','relation_kind_id':kind}},{'path':'fixture-signature','sha256':'3'*64}
reader=N(HERE=Path(FIXTURE_CONFIG['reader']),open_signed=open_signed,adapter=N(CURRENT=('current',),source=N(original=original),eligibility=N(no_private_memory=lambda value:require(type(value)is dict,'FIXTURE_BODY')),model=N(record_bytes=record_bytes,artifact_ref=artifact_ref,signature=signature)))
