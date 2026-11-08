"""Freeze the pre-review API55 receipt after the causal receipt join repair."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v55-t31-engineering-prior-0002'
OLD_SOURCE='44ee9d98bd420065a362783c1ba24f52b811f97f691ce13849b50e5313a29395'
OLD_PROFILE='eff613368a897e4cab02d3b718d6da8ee37f519ccdfb211a8ec11d43e89a97ca'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def binding(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
def save(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')

def main():
    source_path=API/'source-manifest.json';profile_path=API/'contract-profile.json'
    if sha(source_path)!=OLD_SOURCE or sha(profile_path)!=OLD_PROFILE:
        raise ValueError('unreviewed API55 input manifests differ')
    profile=json.loads(profile_path.read_bytes());source=json.loads(source_path.read_bytes())
    changed={name:binding(API/name)for name in ('workflow_transition.py','workflow_prior_input.py')}
    for row in profile['files']:
        for name in changed:
            if row['path']==changed[name]['path']:row['sha256']=changed[name]['sha256']
    save(profile_path,profile)
    changed['contract-profile.json']=binding(profile_path)
    for row in source['files']:
        for name in changed:
            if row['path']==changed[name]['path']:row['sha256']=changed[name]['sha256']
    source['profile_binding']=binding(profile_path)
    save(source_path,source)
    receipt=json.loads((API/'rebind-receipt.json').read_bytes())
    receipt['successor_source_binding']=binding(source_path)
    receipt['successor_profile_binding']=binding(profile_path)
    receipt['prior_contract_binding']=changed['workflow_prior_input.py']
    receipt['cold_repair']='exact selected producer receipt bindings equal committed transaction receipts'
    save(API/'rebind-receipt.json',receipt)
    print(json.dumps({'source_sha256':sha(source_path),'profile_sha256':sha(profile_path)},sort_keys=True))

if __name__=='__main__':main()
