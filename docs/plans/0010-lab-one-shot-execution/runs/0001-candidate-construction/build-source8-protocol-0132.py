"""Construct versioned source-specific protocol resources, preserving all originals."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';API=BASE/'api-v92';PACKAGE=BASE/'source8-protocol-v1'
SCHEMAS=ROOT/'docs/proposals/0007-lab-integrated-schema-package'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes())}
def load(path):return json.loads(path.read_bytes())
def emit(path,value,raw=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(raw if raw is not None else (json.dumps(value,indent=2,sort_keys=True)+'\n').encode())
def replace(path,old,new):
    text=path.read_text();assert old in text,(path,old);path.write_text(text.replace(old,new))

def main():
    shutil.copytree(BASE/'api-v91',API,ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json'))
    shutil.copytree(BASE/'lesson-host-composition-v41',BASE/'lesson-host-composition-v42',ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json'))
    for path in API.glob('*.py'):
        text=path.read_text()
        if 'lesson-host-composition-v41' in text:path.write_text(text.replace('lesson-host-composition-v41','lesson-host-composition-v42'))
    for path in (BASE/'lesson-host-composition-v42').glob('*.py'):
        text=path.read_text()
        if 'api-v91' in text:path.write_text(text.replace('api-v91','api-v92'))
    PACKAGE.mkdir();documents={};origins={}
    # Latest independently selected private schemas win over earlier shared
    # resources with the same original ID, matching the inherited loader.
    folders=[SCHEMAS/'schemas',ROOT/'docs/proposals/0008-lab-api-contracts/schemas',API/'schemas',API]
    for folder in folders:
        for path in sorted(folder.glob('*.schema.json')):
            value=load(path)
            if '$id' in value:documents[value['$id']]=value;origins[value['$id']]=path
    mapping={uri:'urn:cyberalchemy-lab:source8-protocol:'+uri.removeprefix('urn:cyberalchemy-lab:')+':revision-1'
             for uri in documents}
    changes=[]
    def translate(value,path=''):
        if isinstance(value,dict):
            result={}
            for key,item in value.items():
                if key in ('$id','$ref') and isinstance(item,str):
                    root,mark,fragment=item.partition('#');result[key]=mapping.get(root,root)+(mark+fragment if mark else '')
                elif key=='enum' and isinstance(item,list) and 'cal.artifact-type.typed-relation/v3' in item:
                    assert 'cal.artifact-type.typed-relation/v4' not in item
                    result[key]=[*item,'cal.artifact-type.typed-relation/v4'];changes.append(path+'/enum')
                else:result[key]=translate(item,path+'/'+key)
            return result
        if isinstance(value,list):return [translate(item,path+'/'+str(i)) for i,item in enumerate(value)]
        return value
    manifest=[]
    for index,uri in enumerate(sorted(documents)):
        value=translate(documents[uri],uri)
        if uri=='urn:cyberalchemy-lab:protocol:domain-artifact:v1-candidate':
            assert not any(row['properties']['carrier_ref']['const']=='cal.artifact-type.typed-relation/v4' for row in value['oneOf'])
            schema=BASE/'typed-relation-schema-v4/schema.json'
            value['oneOf'].append({'type':'object','additionalProperties':False,'required':['carrier_ref','body'],
                'properties':{'carrier_ref':{'const':'cal.artifact-type.typed-relation/v4'},
                    'body':{'$ref':'urn:cyberalchemy-lab:bound-schema:'+sha(schema.read_bytes())}}})
        path=PACKAGE/'schemas'/f'{index:03d}.schema.json';emit(path,value)
        manifest.append({'original_uri':uri,'selected_uri':value['$id'],'source_binding':bind(origins[uri]),'selected_binding':bind(path)})
    snapshot=BASE/'current-participation-v8/packages/0001/branch.snapshot';snap=load(snapshot)
    txrow=snap['files']['transactions/0000000004.json'];txraw=base64.b64decode(txrow['base64_original_bytes'],validate=True)
    assert sha(txraw)==txrow['sha256'];target=json.loads(txraw)['proposal']['targets'][0]
    assert target['version_ref']=='cal.artifact-type.typed-relation/v4'
    original=base64.b64decode(target['content']['data'],validate=True)
    assert sha(original)==target['content']['byte_sha256'] and json.loads(original)==target['record']
    descriptor=PACKAGE/'signed-local-declaration.json';emit(descriptor,None,raw=original)
    plan=load(BASE/'current-participation-v8/packages/0001/resolution-qualification-plan.json')
    record={'schema_version':'lab-source8-signed-catalog-declaration/v1-candidate',
        'represented_contract_ref':target['version_ref'],'identity_ref':target['version_ref'].rsplit('/',1)[0],
        'meta_carrier_ref':target['carrier_ref'],'source_cut':plan['source_cut'],
        'source_snapshot_binding':bind(snapshot),'source_package_binding':bind(snapshot.parent/'manifest.json'),
        'transaction_binding':{'ref':'store:R03-current-participation-0008:transactions/0000000004.json','sha256':sha(txraw)},
        'declaration_binding':bind(descriptor),'body':target['record'],
        'instance_schema_binding':{'ref':target['record']['schema_path'],'sha256':target['record']['schema_sha256']},
        'authority_effect':'none','actual_owner_outcome':None}
    emit(PACKAGE/'catalog-declaration.json',record)
    schema=BASE/'typed-relation-schema-v4/schema.json'
    emit(PACKAGE/'selection.json',{'schema_version':'lab-source8-protocol-selection/v1-candidate',
        'resources':manifest,'uri_mapping':mapping,'exact_added_carriers':['cal.artifact-type.typed-relation/v4'],
        'carrier_enum_changed_selectors':changes,'additional_domain_binding':bind(schema),
        'catalog_declaration_binding':bind(PACKAGE/'catalog-declaration.json'),
        'source_binding':bind(BASE/'current-participation-v8/source-manifest.json'),
        'package_binding':bind(snapshot.parent/'manifest.json'),'authority_effect':'none','actual_owner_outcome':None,
        'claim_ceiling':'Versioned closed candidate wire resource eligibility for exact signed Source8 carrier/declaration; no canonical admission or authority grant.'})
    # Local validators read their own raw schemas; select the same versioned
    # resources explicitly, rather than replacing original registry IDs.
    for folder in (API,API/'schemas'):
        for path in folder.glob('*.schema.json'):
            value=load(path);path.write_text(json.dumps(translate(value),indent=2,sort_keys=True)+'\n')
    print(json.dumps({'result':'CONSTRUCTED','resources':len(manifest),'carrier_enum_extensions':len(changes),
        'selection_binding':bind(PACKAGE/'selection.json'),'api':str(API)}))

if __name__=='__main__':main()
