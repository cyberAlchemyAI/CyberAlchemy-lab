#!/usr/bin/env python3
"""Independent normative/artifact checks only; no product import or execution.
Open Questions: README.md#open-questions.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[6]
def require(ok,message):
    if not ok: raise ValueError(message)
def load(name): return json.loads((BASE/name).read_text())
def digest(file): return hashlib.sha256(file.read_bytes()).hexdigest()
def duplicate_free(rows):
    out={}
    for key,value in rows:
        if key in out: raise ValueError('decoded duplicate member')
        out[key]=value
    return out
def scalar_strings(value):
    if isinstance(value,str): require(all(not 0xd800<=ord(c)<=0xdfff for c in value),'lone surrogate')
    elif isinstance(value,dict):
        for k,v in value.items(): scalar_strings(k);scalar_strings(v)
    elif isinstance(value,list):
        for v in value:scalar_strings(v)
def wire_value(data):
    text=data.decode('utf-8','strict')
    value=json.loads(text,object_pairs_hook=duplicate_free,parse_constant=lambda _value:(_ for _ in ()).throw(ValueError('non-JSON constant')))
    scalar_strings(value)
    require(type(value) is dict and set(value)=={'id','verified'},'exact flat input fields')
    require(type(value['id']) is str and type(value['verified']) is bool,'exact string and Bool')
    require(len(value['id'])<=20 and re.fullmatch(r'(0|[1-9][0-9]*)',value['id']) is not None,'canonical decimal')
    require(int(value['id'])<=18446744073709551615,'UInt64 overflow')
    return {'id_decimal':value['id'],'verified':value['verified']}
def validate():
    for row in load('sources.json')['files']:
        file=ROOT/row['path'];require(file.is_file() and digest(file)==row['sha256'] and file.stat().st_size==row['bytes'],'normative source identity drift: '+row['path'])
    original=ROOT/'craft/projects/domainspec-v2/impl/cli/test/profile-engine/fixtures/u0-v2'
    for name in ['wire-vectors.json','identity-vectors.json']:
        require((BASE/name).read_bytes()==(original/name).read_bytes(),'pre-implementation literal changed: '+name)
    wire=load('wire-vectors.json')
    require(wire['configuration']=={'request_bytes':4096,'response_bytes':1024,'body_timeout_ms':2000},'selected configuration')
    require(len(wire['decoder'])==34 and len(wire['media'])==9 and len(wire['encoder'])==2,'C03 inventory')
    for row in wire['decoder']:
        try:actual=wire_value(bytes.fromhex(row['bytes_hex']))
        except (ValueError,TypeError,UnicodeError):actual=None
        if row['expected']['kind']=='decoded':require(actual==row['expected']['value'],'literal decoder/formation oracle mismatch: '+row['id'])
        else:require(actual is None,'invalid-request literal contradiction: '+row['id'])
    for row in wire['encoder']:
        require(json.loads(row['canonical'])==row['value'],'literal encoding shape')
        require(len(row['canonical'].encode())==row['bytes'],'literal encoder byte bound')
    identity=load('identity-vectors.json')['vectors'];require(len(identity)==3,'C02 identity inventory')
    for row in identity:
        for stage in ['executable','assurance','review']:
            require(hashlib.sha256(row['expected'][stage+'_canonical'].encode()).hexdigest()==row['expected'][stage+'_sha256'],'independent canonical digest')
    require(len({row['expected']['executable_sha256'] for row in identity})==1,'claim-only executable invariance')
    require(len({row['expected']['assurance_sha256'] for row in identity})==3,'separate assurance identity')
    http=load('http-oracles.json')['cases'];require(len(http)==22,'HTTP inventory')
    for row in http:
        require(row['response_bytes']==len(row['response'].encode()),'literal response count')
        response=json.loads(row['response']);require(row['response_media']=='application/json; charset=utf-8','response media')
        require(row['invoked']==(row['status'] in [200,422]),'invocation boundary')
        require(row['acquisition_started']==(row['status'] not in [404,405,415]),'preflight acquisition boundary')
        require(row['evidence_ceiling']=='local-settlement-only','no delivery claim')
        if row['status'] in [200,422]:
            value=wire_value(row['body'].encode())
            if row['status']==200:
                require(value['verified'] is True and response=={'kind':'completed','value':{'id':value['id_decimal'],'verified':True}},'literal business result')
            else:
                require(value['verified'] is False and response=={'kind':'rejected','code':'delivery-verification-required'},'literal business rejection')
        else:
            require(response['kind']=='adapter-error' and row['invoked'] is False,'adapter/business separation')
            if row['status']==400:
                try:wire_value(row['body'].encode())
                except (ValueError,TypeError,UnicodeError):pass
                else:raise ValueError('malformed wire fixture became valid')
    acq=load('acquisition-oracles.json');require(len(acq['cases'])==14,'acquisition inventory')
    for row in acq['cases']:
        require(json.loads(row['response'])=={'kind':'adapter-error','code':row['code']},'literal acquisition error')
        require(row['cleanup']=={'reader_released':True,'timer_clear_count_if_started':1,'abort_listener_removed_if_added':True},'conditional cleanup')
        require(row['scope']==('component-containment-only' if row['id']=='invalid-native-outcome' else 'actual-selected-handler'),'no fake business error')
    for row in acq['positive_boundaries']:
        if 'canonical' in row:require(len(row['canonical'].encode())==row['bytes'],'canonical maximum')
    custody=load('custody-output-inventory.json');require(len(custody['cases'])==52,'custody/output/source inventory')
    for row in custody['cases']:
        require(row['required_u0'] is True and row['business_callbacks_allowed'] is False and row['acceptance_refs'],'fixture scope')
    require(len(custody['separate_unselected_scope'])==6,'unselected formal/auth/effect/target/operational scope')
    groups={'decoder':wire['decoder'],'media':wire['media'],'encoder':wire['encoder'],'identity':identity,'http':http,'acquisition':acq['cases'],'boundaries':acq['positive_boundaries'],'custody-output':custody['cases']}
    ids=[]
    for group,rows in groups.items():
        for i,row in enumerate(rows):ids.append(group+':'+row.get('id',str(i)))
    require(len(ids)==len(set(ids)),'duplicate fixed case identity')
    if (BASE/'case-inventory.json').exists():require(load('case-inventory.json')['case_ids']==ids,'fixed runner inventory drift')
    return {'scope':'independent literal/math/source artifact validation only','product_runtime_executed':False,'authority_effect':'none','counts':{group:len(rows) for group,rows in groups.items()},'total_fixed_cases':len(ids),'case_ids':ids,'runtime_qualification':'pending G01/U08/V01/V02/H01/F00/V03','open_questions_ref':'README.md#open-questions'}
if __name__=='__main__':
    report=validate()
    if '--seal' in sys.argv:
        require(not (BASE/'oracle-identities.json').exists(),'oracle already sealed; preserve old epoch')
        (BASE/'case-inventory.json').write_text(json.dumps({'schema_version':'craft.u0-fixed-case-inventory/v1-candidate','case_ids':report['case_ids'],'authority_effect':'none','open_questions_ref':'README.md#open-questions'},indent=2)+'\n')
        rows=[{'path':p.name,'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(BASE.iterdir()) if p.is_file() and p.name!='oracle-identities.json']
        (BASE/'oracle-identities.json').write_text(json.dumps({'schema_version':'craft.u0-oracle-identities/v1-candidate','authority_effect':'none','files':rows,'expected_values_origin':'sealed pre-implementation C02/C03 and normative acceptance; no producer-derived expected responses','observation_status':'not-observed-by-V00','open_questions_ref':'README.md#open-questions'},indent=2)+'\n')
    manifest=load('oracle-identities.json')['files']
    require({r['path'] for r in manifest}=={p.name for p in BASE.iterdir() if p.is_file() and p.name!='oracle-identities.json'},'oracle closure inventory')
    for row in manifest:
        p=BASE/row['path'];require(digest(p)==row['sha256'] and p.stat().st_size==row['bytes'],'fixed oracle byte drift: '+row['path'])
    print(json.dumps({k:v for k,v in report.items() if k!='case_ids'},indent=2))
