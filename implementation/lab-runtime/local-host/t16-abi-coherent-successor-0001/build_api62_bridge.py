"""Recut API61 into a source-pinned coherent custody alias candidate."""
import ast, hashlib, json, os, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v61-t16-abi423-bridge-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v62-t16-abi423-alias-0001'
FAMILY=ROOT/'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0'
OLD_SOURCE='84435a57c990a1d85504cf844a257e6dc3607c81519d368c828449ac8106ffc4'
OLD_PROFILE='843ee830613211f6c36c6c822ef32b08e71b5799166485ed24b99d09f053e12c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
bytes_json=lambda v:(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}

def main():
    os.umask(0o077)
    if NEW.exists() or sha(OLD/'source-manifest.json')!=OLD_SOURCE or sha(OLD/'contract-profile.json')!=OLD_PROFILE:
        raise ValueError('predecessor differs or successor exists')
    profile=json.loads((OLD/'contract-profile.json').read_bytes())
    source=json.loads((OLD/'source-manifest.json').read_bytes())
    if len(profile['files'])!=33425 or len(source['files'])!=210:
        raise ValueError('source/profile inventory differs')
    NEW.mkdir(mode=0o700)
    for p in OLD.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.name in ('source-manifest.json','contract-profile.json','rebind-receipt.json'):
            continue
        dest=NEW/p.relative_to(OLD)
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,dest)
    bridge=NEW/'source_bridge.py'
    text=bridge.read_text().replace('_cal_api61_t16_legacy_local_20261023_0001','_cal_api62_t16_legacy_local_20261023_0001').replace('_cal_api61_t16_source8_local_20261023_0001','_cal_api62_t16_source8_local_20261023_0001')
    ast.parse(text);bridge.write_text(text)
    scopes=NEW/'guarded_candidate.py'
    text=scopes.read_text()
    old='from .custody_context_sessions import PermissionBridge,BOUNDARIES,DELIVERY_PIN'
    if text.count(old)!=2:raise ValueError('custody alias selection scopes changed')
    text=text.replace(old,'from .current_legacy_context_sessions import PermissionBridge,BOUNDARIES,DELIVERY_PIN')
    ast.parse(text);scopes.write_text(text)
    registry=NEW/'workflow_output_registry.py'
    text=registry.read_text().replace(OLD.name,NEW.name)
    ast.parse(text);registry.write_text(text)
    # Inherited test source is deliberately byte-identical and retains all ASTs.
    for p in OLD.glob('test_*.py'):
        if sha(p)!=sha(NEW/p.name):raise ValueError('inherited test AST bytes differ: '+p.name)
    for p in OLD.glob('run_*checks.py'):
        if sha(p)!=sha(NEW/p.name):raise ValueError('inherited run-check AST bytes differ: '+p.name)
    old_prefix=OLD.relative_to(ROOT).as_posix()+'/'
    new_prefix=NEW.relative_to(ROOT).as_posix()+'/'
    def recut(row):
        if row['path'].startswith(old_prefix):
            return binding(NEW/row['path'][len(old_prefix):])
        return row
    profile['files']=sorted([recut(row) for row in profile['files']],key=lambda r:r['path'])
    for key,value in list(profile.items()):
        if key!='files' and isinstance(value,dict) and set(value)=={'path','sha256'}:
            profile[key]=recut(value)
    profile['claim_ceiling']='Local current-family historical bridge candidate; inherited methods require complete execution and separate qualification.'
    (NEW/'contract-profile.json').write_bytes(bytes_json(profile))
    source['files']=sorted([recut(row) for row in source['files']],key=lambda r:r['path'])
    source['profile_binding']=binding(NEW/'contract-profile.json')
    source['predecessor_source_manifest_binding']=binding(OLD/'source-manifest.json')
    source['claim_ceiling']='Local current-family bridge and inherited AST preservation; no complete T16 qualification or authority effect.'
    (NEW/'source-manifest.json').write_bytes(bytes_json(source))
    receipt={'schema_version':'lab-T16-API62-coherent-custody-alias/v1-candidate',
             'predecessor_source_binding':binding(OLD/'source-manifest.json'),
             'successor_source_binding':binding(NEW/'source-manifest.json'),
             'successor_package':NEW.relative_to(ROOT).as_posix(),
             'successor_manifest_sha256':sha(NEW/'source-manifest.json'),
             'successor_profile_binding':binding(NEW/'contract-profile.json'),
             'fresh_family_source_binding':binding(FAMILY/'source/source-manifest.json'),
             'fresh_family_context_binding':binding(FAMILY/'context/source-manifest.json'),
             'inherited_test_files_byte_identical':True,'custody_alias_guard_scopes':'fresh-current-legacy','authority_effect':'none',
             't16_qualified':False}
    (NEW/'rebind-receipt.json').write_bytes(bytes_json(receipt))
    print(json.dumps({'api_source_binding':receipt['successor_source_binding'],
                      'api_profile_binding':receipt['successor_profile_binding'],
                      'inherited_test_files_byte_identical':True},sort_keys=True))

if __name__=='__main__': main()
