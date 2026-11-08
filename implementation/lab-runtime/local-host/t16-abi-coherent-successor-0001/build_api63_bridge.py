"""Recut API62 into coherent current-family custody and legacy aliases."""
import ast, hashlib, json, os, shutil, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v62-t16-abi423-alias-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v63-t16-abi423-alias-0001'
FAMILY=ROOT/'implementation/lab-runtime/local-host/t16-abi-coherent-successor-0001/instances/legacy-local-e084574c6d149cf0'
OLD_SOURCE='9c39d58572139a731d610bb0cf174655892106b805985567762c2041a98b94be'
OLD_PROFILE='c98076fd86b3fced1d7b356017efd234c0205b62c7f357a28419d709d56e5258'
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
    text=bridge.read_text()
    text=text.replace('_cal_api62_t16_legacy_local_20261023_0001','_cal_api63_t16_legacy_local_20261023_0001').replace('_cal_api62_t16_source8_local_20261023_0001','_cal_api63_t16_source8_local_20261023_0001')
    if len(re.findall(r'(?<![A-Za-z0-9_])legacy_delivery\(\)',text))!=5 or text.count('def legacy_delivery():')!=1:
        raise ValueError('legacy delivery call/definition inventory changed')
    text=re.sub(r'(?<![A-Za-z0-9_])legacy_delivery\(\)','expired_legacy_delivery()',text)
    text=text.replace('def expired_legacy_delivery():', 'def legacy_delivery():\n    return current_legacy_delivery()\n\ndef expired_legacy_delivery():')
    old='            selected.view.custody_signed_sources=selected\n            yield selected.view'
    new='            selected.view.custody_signed_sources=selected\n            selected.view.legacy_signed_sources=selected\n            selected.view.legacy_context_producer=d\n            selected.view.integrated_reader=d.reader\n            yield selected.view'
    if text.count(old)!=1:raise ValueError('custody alias marker changed')
    text=text.replace(old,new)
    ast.parse(text);bridge.write_text(text)
    legacy_runtime=NEW/'legacy_context_sessions.py'
    text=legacy_runtime.read_text().replace('D=source.legacy_delivery()','D=source.expired_legacy_delivery()')
    ast.parse(text);legacy_runtime.write_text(text)
    runtime=NEW/'current_legacy_context_sessions.py'
    text=runtime.read_text()
    old="channel.policy['source_name']==source.CURRENT_LEGACY_NAME"
    if text.count(old)!=1:raise ValueError('current Context policy alias changed')
    text=text.replace(old,"channel.policy['source_name'] in (source.CURRENT_LEGACY_NAME,'custody-participation')")
    ast.parse(text);runtime.write_text(text)
    auth=NEW/'auth.py'
    text=auth.read_text()
    old="else ROOT/'product/lab/release-candidates/v1/interface/current-participation-v5/packages/0001/period.json'"
    if text.count(old)!=1:raise ValueError('custody termination period selection changed')
    text=text.replace(old,"else ROOT/source.CURRENT_LEGACY_SOURCE/'packages/0001/period.json'")
    ast.parse(text);auth.write_text(text)
    machine=NEW/'machine_auth_scope.py'
    text=machine.read_text()
    old="owner.channel.policy['source_name']=='completion-legacy:legacy-local-e084574c6d149cf0'"
    if text.count(old)!=1:raise ValueError('Machine current legacy policy selection changed')
    text=text.replace(old,"owner.channel.policy['source_name'] in ('completion-legacy:legacy-local-e084574c6d149cf0','custody-participation')")
    ast.parse(text);machine.write_text(text)
    service=NEW/'service.py'
    text=service.read_text()
    text=text.replace('from .custody_context_sessions import ContextSessions','from .current_legacy_context_sessions import ContextSessions')
    text=text.replace('from .custody_context_sessions import MachineContextSessions','from .current_legacy_context_sessions import MachineContextSessions')
    ast.parse(text);service.write_text(text)
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
    receipt={'schema_version':'lab-T16-API63-coherent-family-alias/v1-candidate',
             'predecessor_source_binding':binding(OLD/'source-manifest.json'),
             'successor_source_binding':binding(NEW/'source-manifest.json'),
             'successor_package':NEW.relative_to(ROOT).as_posix(),
             'successor_manifest_sha256':sha(NEW/'source-manifest.json'),
             'successor_profile_binding':binding(NEW/'contract-profile.json'),
             'fresh_family_source_binding':binding(FAMILY/'source/source-manifest.json'),
             'fresh_family_context_binding':binding(FAMILY/'context/source-manifest.json'),
             'inherited_test_files_byte_identical':True,'custody_alias_guard_scopes':'fresh-current-legacy','custody_alias_session_runtime':'fresh-current-legacy','authority_effect':'none',
             't16_qualified':False}
    (NEW/'rebind-receipt.json').write_bytes(bytes_json(receipt))
    print(json.dumps({'api_source_binding':receipt['successor_source_binding'],
                      'api_profile_binding':receipt['successor_profile_binding'],
                      'inherited_test_files_byte_identical':True},sort_keys=True))

if __name__=='__main__': main()
