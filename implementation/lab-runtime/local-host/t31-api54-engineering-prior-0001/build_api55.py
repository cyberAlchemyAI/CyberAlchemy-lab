"""No-replace API55 successor: exact original producer principal join."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v54-t31-engineering-prior-0001'
NEW=BASE/'api-integration-v55-t31-engineering-prior-0002'
OLD_ADAPTER=ROOT/'implementation/lab-runtime/local-host/t31-api54-engineering-bootstrap-0001/bootstrap.py'
NEW_ADAPTER=ROOT/'implementation/lab-runtime/local-host/t31-api55-engineering-bootstrap-0002/bootstrap.py'
SOURCE_SHA='030cadf77f52b44d6f83d4004c74d21e7c0cfd8443de33110cdd98c0ad989e44'
PROFILE_SHA='a38cd23816cbf8e624fd1b44913c3b84af9f7fb52faa864727c59eab2e3c2dbe'
HELPER=Path(__file__).with_name('prior_contract.py')
CLAIM=('API55 exact engineering template and committed prior design output with producer Principal join; '
       'cold only, no signed-Source admission of produced output, actual transition, owner outcome or count increment.')
def raw(path):return Path(path).read_bytes()
def sha(body):return hashlib.sha256(body).hexdigest()
def row(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(raw(path))}
def replace(value,old,new,n=1):
    if value.count(old)!=n:raise ValueError('exact recut anchor differs: '+old[:80])
    return value.replace(old,new)
def save(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')

def main():
    if sha(raw(OLD/'source-manifest.json'))!=SOURCE_SHA or sha(raw(OLD/'contract-profile.json'))!=PROFILE_SHA:
        raise ValueError('frozen API54 predecessor changed')
    if NEW.exists() or NEW_ADAPTER.exists():raise ValueError('API55 already exists')
    manifest=json.loads(raw(OLD/'source-manifest.json'));profile=json.loads(raw(OLD/'contract-profile.json'))
    op=OLD.relative_to(ROOT).as_posix()+'/';np=NEW.relative_to(ROOT).as_posix()+'/'
    own=[v for v in manifest['files']if v['path'].startswith(op)]
    if len(manifest['files'])!=212 or len(own)!=202 or len(profile['files'])!=33429:raise ValueError('API54 inventory differs')
    physical={p.relative_to(OLD).as_posix()for p in OLD.rglob('*')if p.is_file()and p.name not in ('source-manifest.json','rebind-receipt.json')and '__pycache__'not in p.parts and p.suffix!='.pyc'}
    if physical!={v['path'][len(op):]for v in own}:raise ValueError('API54 physical closure differs')
    for v in own:
        if sha(raw(OLD/v['path'][len(op):]))!=v['sha256']:raise ValueError('API54 byte changed')
    changed={}
    n='workflow-output-plan.schema.json';changed[n]=replace(raw(OLD/n).decode(),op+'service.py',np+'service.py',2).encode()
    n='workflow_output_registry.py';changed[n]=replace(raw(OLD/n).decode(),op+'workflow_',np+'workflow_',7).encode()
    n='source_bridge.py';v=raw(OLD/n).decode();v=replace(v,'_cal_api54_t31_legacy_local_20261023_0001','_cal_api55_t31_legacy_local_20261023_0001');v=replace(v,'_cal_api54_t31_source8_local_20261023_0001','_cal_api55_t31_source8_local_20261023_0001');changed[n]=v.encode()
    n='guard.py';changed[n]=replace(raw(OLD/n).decode(),OLD_ADAPTER.relative_to(ROOT).as_posix(),NEW_ADAPTER.relative_to(ROOT).as_posix()).encode()
    n='workflow_transition.py';v=replace(raw(OLD/n).decode(),
        'transaction=transaction,result=result,row=rows[0],header=header)',
        "transaction=transaction,result=result,producer_principal=result._authorization.packet['principal_ref'],row=rows[0],receipts=receipts,header=header)")
    changed[n]=replace(v,"        rows,_=result.material.selected(route['output_slot_ref'])",
                       "        rows,receipts=result.material.selected(route['output_slot_ref'])").encode()
    n='workflow_prior_input.py';changed[n]=raw(HELPER)
    adapter=replace(raw(OLD_ADAPTER).decode(),OLD.name,NEW.name)
    NEW_ADAPTER.parent.mkdir(parents=True,mode=0o700);NEW_ADAPTER.write_text(adapter)
    NEW.mkdir(mode=0o700)
    for v in own:
        name=v['path'][len(op):]
        if name=='contract-profile.json':continue
        target=NEW/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(changed.get(name,raw(OLD/name)))
    profile['files']=sorted([row(NEW/v['path'][len(op):])if v['path'].startswith(op)else row(NEW_ADAPTER)if v['path']==OLD_ADAPTER.relative_to(ROOT).as_posix()else v for v in profile['files']],key=lambda v:v['path'])
    if len({v['path']for v in profile['files']})!=len(profile['files']):raise ValueError('duplicate profile row')
    profile['integration_members_binding']=row(NEW/'integration-members.json');profile['claim_ceiling']=CLAIM
    save(NEW/'contract-profile.json',profile)
    manifest['files']=sorted([row(NEW/v['path'][len(op):])if v['path'].startswith(op)else row(NEW_ADAPTER)if v['path']==OLD_ADAPTER.relative_to(ROOT).as_posix()else v for v in manifest['files']],key=lambda v:v['path'])
    if len({v['path']for v in manifest['files']})!=len(manifest['files']):raise ValueError('duplicate Source row')
    manifest['profile_binding']=row(NEW/'contract-profile.json')
    manifest['predecessor_source_manifest_binding']=row(OLD/'source-manifest.json')
    manifest['claim_ceiling']=CLAIM
    save(NEW/'source-manifest.json',manifest)
    save(NEW/'rebind-receipt.json',{'schema_version':'lab-T31-API55-prior-principal/v1-candidate',
         'predecessor_source_binding':row(OLD/'source-manifest.json'),
         'successor_source_binding':row(NEW/'source-manifest.json'),
         'successor_profile_binding':row(NEW/'contract-profile.json'),
         'prior_contract_binding':row(NEW/'workflow_prior_input.py'),
         'adapter_binding':row(NEW_ADAPTER),'source_files':len(manifest['files']),
         'profile_files':len(profile['files']),'actual_workflow_transitions':0,
         'authority_effect':'none','claim_ceiling':CLAIM})
    print(json.dumps({'source_sha256':sha(raw(NEW/'source-manifest.json')),
                      'profile_sha256':sha(raw(NEW/'contract-profile.json')),
                      'source_files':len(manifest['files']),'profile_files':len(profile['files'])},sort_keys=True))

if __name__=='__main__':main()
