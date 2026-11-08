"""Disjoint API55 recut selecting W03 for legacy workflow, retaining ce4 Source8."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v55-t31-engineering-prior-0002'
NEW = BASE / 'api-integration-v56-t31-w03-current-0001'
OLD_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api55-engineering-bootstrap-0002/bootstrap.py'
NEW_ADAPTER = ROOT / 'implementation/lab-runtime/local-host/t31-api56-w03-current-0001/bootstrap.py'
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-8d0312c813444f57'
OLD_FAMILY = 'legacy-local-ce4d53a6479188a5'
NEW_FAMILY = 'legacy-local-8d0312c813444f57'
SOURCE_SHA = 'be60601a880fa643f6cb6afb20294a85d305cb576fec9e1e2ccadfc0e74055a3'
PROFILE_SHA = 'eb0829cce7b537b0a0ab7c226f7a4d474b22acb4acd8c4a1fe50dc9ed040eaf1'
PINS = {
    'source/source-manifest.json': '14639c94bd192ebbaf0f34524e588bf7b09ea75616e2b10bbe53df98695833d6',
    'source/packages/0001/manifest.json': 'b78fe83c69e40457b891550540873c62a53294d671d7622807d2129600766d27',
    'reader-w03-0002/source-manifest.json': '0cd65a9e171dd5e41afe719b52ad61fef7c7365491df1b31f9d594c7b2824081',
    'mapped-w03-0004/source-manifest.json': 'b19214cb65d40ed39adc6c413a0f6dbda2b9d77dd9025ef9f8301aec6859b04c',
    'mapped-w03-0004/packages/0001/manifest.json': '06860ad635e2bce7c3e302f97e4d977330df4f72a2e0b5d363965a51cdcb0414',
    'context-w03-0005/source-manifest.json': '1431ae034790ed477f533a9d00fd21924817f93ff313a50ae2b940685f202d87',
    'context-w03-0005/packages/0001/manifest.json': '8a719c7c3bb1f1fc9edd5c7b258ed0d508bae7d14b7a95245a3b67755ba7a8a2',
}
OLD_CONTEXT_SHA = '07fd3184fc4d68c955886dca2f787e8bc8f82c46b6f892e2cebdc02a09e667ec'
MAPPING_SHA = 'f38aa25daede03cccfac0e8b64a5ad49fa2e7017df343a4cd5aadd180eb5348d'
NATIVE_TEMPLATE_SHA = '036b74ed9e9456358f8c5117b2026cf0a29240c7c43b67d97148e05a5ac3afe7'
CLAIM = ('W03 exact local signed Source and current legacy workflow fixture selected; '
         'no original engineering transition, later consumer, admission or owner outcome yet.')


def raw(path): return Path(path).read_bytes()
def sha(body): return hashlib.sha256(body).hexdigest()
def row(path):
    if not path.is_file() or path.is_symlink() or not path.is_relative_to(ROOT):
        raise ValueError('unsafe selected API56 file')
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(raw(path))}
def save(path,value): path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
def replace(text,old,new,count):
    if text.count(old)!=count: raise ValueError('API56 exact anchor differs: '+old[:80]+' count='+str(text.count(old)))
    return text.replace(old,new)


def recut(name,text):
    old=OLD.name;new=NEW.name
    if name in ('workflow-output-plan.schema.json','workflow_output_registry.py'):
        return text.replace(old,new)
    if name=='guard.py':
        return replace(text,OLD_ADAPTER.relative_to(ROOT).as_posix(),NEW_ADAPTER.relative_to(ROOT).as_posix(),1)
    if name=='native_dispositions.py':
        template = ROOT / 'implementation/lab-runtime/local-host/t31-api56-w03-current-0001/native_dispositions_w03.py'
        if template.is_symlink() or not template.is_file() or sha(raw(template))!=NATIVE_TEMPLATE_SHA:
            raise ValueError('W03 native-disposition constructor differs')
        return raw(template).decode()
    if name in ('handlers.py','projection.py'):
        return replace(text,'native.REASON','native.reason(view)',1)
    if name=='authentication.schema.json':
        return text.replace('completion-legacy:'+OLD_FAMILY,'completion-legacy:'+NEW_FAMILY)
    if name=='current_legacy_context_sessions.py':
        return text.replace(OLD_FAMILY,NEW_FAMILY)
    if name=='legacy_fixture_selection.py':
        text=text.replace(OLD_FAMILY,NEW_FAMILY)
        text=text.replace('/'+NEW_FAMILY+'/reader','/'+NEW_FAMILY+'/reader-w03-0002')
        text=replace(text,"EXPECTED_NOT_BEFORE='2026-10-23T06:04:25.580913+00:00'","EXPECTED_NOT_BEFORE='2026-10-23T12:00:48+00:00'",1)
        text=replace(text,"EXPECTED_EXPIRES_AT='2026-10-24T06:04:25.580913+00:00'","EXPECTED_EXPIRES_AT='2026-10-24T12:00:48+00:00'",1)
        return text
    if name=='machine_auth_scope.py':
        old_path='/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source8-current-fixture/instances/'+OLD_FAMILY+'/context'
        new_path='/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/source8-current-fixture/instances/'+NEW_FAMILY+'/context-w03-0005'
        text=replace(text,"'current_legacy_context_sessions.py':('"+old_path+"',\n        '"+OLD_CONTEXT_SHA+"')",
                     "'current_legacy_context_sessions.py':('"+new_path+"',\n        '"+PINS['context-w03-0005/source-manifest.json']+"')",1)
        text=text.replace('completion-legacy:'+OLD_FAMILY,'completion-legacy:'+NEW_FAMILY)
        text=replace(text,"'completion-legacy-local-"+OLD_FAMILY.split('legacy-local-')[1]+"'",
                     "'completion-legacy-local-"+NEW_FAMILY.split('legacy-local-')[1]+"'",1)
        return replace(text,"'branch:completion-legacy-local-"+OLD_FAMILY.split('legacy-local-')[1]+"'",
                       "'branch:completion-legacy-local-"+NEW_FAMILY.split('legacy-local-')[1]+"'",1)
    if name=='source_bridge.py':
        start=text.index('def current_workflow_bindings():')
        end=text.index('def legacy_profile_binding(',start)
        block=text[start:end].replace(OLD_FAMILY,NEW_FAMILY)
        block=block.replace('/'+NEW_FAMILY+'/reader/source-manifest.json',
                            '/'+NEW_FAMILY+'/reader-w03-0002/source-manifest.json')
        block=block.replace('b3461a1e68a5da06ad6c47966eb4ed448e67f2318baf5e7e956937d15f007877',PINS['reader-w03-0002/source-manifest.json'])
        block=block.replace('0dc869f614e4d1f4be29c4b85f60dd5abd8f25b9fe84e1dc779932aee90c50d4',PINS['source/source-manifest.json'])
        block=block.replace('7006fd4fac3327b76f4ffcc03d93ffb070bb25288ca7bab7e7e5b20470baf22c',PINS['source/packages/0001/manifest.json'])
        text=text[:start]+block+text[end:]
        text=replace(text,"CURRENT_LEGACY_NAME='completion-legacy:"+OLD_FAMILY+"'",
                     "CURRENT_LEGACY_NAME='completion-legacy:"+NEW_FAMILY+"'",1)
        text=replace(text,"CURRENT_LEGACY_STORE='completion-"+OLD_FAMILY+"'",
                     "CURRENT_LEGACY_STORE='completion-"+NEW_FAMILY+"'",1)
        for leaf in ('CONTEXT','READER','SOURCE'):
            old_line="CURRENT_LEGACY_"+leaf+"='implementation/lab-runtime/local-host/source8-current-fixture/instances/"+OLD_FAMILY+"/"+('context' if leaf=='CONTEXT' else leaf.lower())+"'"
            new_line="CURRENT_LEGACY_"+leaf+"='implementation/lab-runtime/local-host/source8-current-fixture/instances/"+NEW_FAMILY+"/"+('context-w03-0005' if leaf=='CONTEXT' else 'reader-w03-0002' if leaf=='READER' else leaf.lower())+"'"
            text=replace(text,old_line,new_line,1)
        text=replace(text,"CURRENT_LEGACY_DELIVERY_PIN='"+OLD_CONTEXT_SHA+"'",
                     "CURRENT_LEGACY_DELIVERY_PIN='"+PINS['context-w03-0005/source-manifest.json']+"'",1)
        text=replace(text,"'_cal_api55_t31_legacy_local_20261023_0001'","'_cal_api56_t31_w03_legacy_20261023_0001'",1)
        return text
    return text


def family_rows():
    rows={}
    for leaf,pin in PINS.items():
        path=FAMILY/leaf
        if row(path)['sha256']!=pin: raise ValueError('W03 exact family pin differs: '+leaf)
        rows[row(path)['path']]=row(path)
        selected=json.loads(raw(path))
        for item in selected.get('files',[]):
            source_path=ROOT/item['path']
            if row(source_path)!=item: raise ValueError('W03 selected family file differs: '+item['path'])
            rows[item['path']]=item
    return rows


def main():
    if sha(raw(OLD/'source-manifest.json'))!=SOURCE_SHA or sha(raw(OLD/'contract-profile.json'))!=PROFILE_SHA:
        raise ValueError('API55 predecessor differs')
    if NEW.exists() or NEW_ADAPTER.exists(): raise ValueError('API56 successor exists')
    family=family_rows()
    manifest=json.loads(raw(OLD/'source-manifest.json'))
    profile=json.loads(raw(OLD/'contract-profile.json'))
    op=OLD.relative_to(ROOT).as_posix()+'/';np=NEW.relative_to(ROOT).as_posix()+'/'
    own=[item for item in manifest['files'] if item['path'].startswith(op)]
    if len(manifest['files'])!=212 or len(own)!=202 or len(profile['files'])!=33429:
        raise ValueError('API55 source/profile cardinality differs')
    expected={item['path'][len(op):] for item in own}
    physical={path.relative_to(OLD).as_posix() for path in OLD.rglob('*') if path.is_file()
              and path.name not in ('source-manifest.json','rebind-receipt.json')
              and '__pycache__' not in path.parts and path.suffix!='.pyc'}
    if expected!=physical: raise ValueError('API55 selected physical own-source differs')
    for item in own:
        path=OLD/item['path'][len(op):]
        if row(path)!=item: raise ValueError('API55 own-source digest differs')
    NEW_ADAPTER.parent.mkdir(parents=True,exist_ok=True)
    NEW_ADAPTER.write_text(raw(OLD_ADAPTER).decode().replace(OLD.name,NEW.name))
    NEW.mkdir()
    for item in own:
        leaf=item['path'][len(op):]
        if leaf=='contract-profile.json': continue
        source_path=OLD/leaf
        selected=raw(source_path)
        if source_path.suffix in ('.py','.json') and leaf!='source-manifest.json':
            selected=recut(leaf,selected.decode()).encode()
        target=NEW/leaf;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(selected)
    profile_rows={item['path']:item for item in profile['files']}
    for item in own:
        profile_rows.pop(item['path'],None)
        if item['path'].endswith('/contract-profile.json'):continue
        current=row(NEW/item['path'][len(op):]);profile_rows[current['path']]=current
    old_adapter_path=OLD_ADAPTER.relative_to(ROOT).as_posix()
    if old_adapter_path not in profile_rows: raise ValueError('API55 adapter absent from profile')
    profile_rows.pop(old_adapter_path)
    profile_rows[row(NEW_ADAPTER)['path']]=row(NEW_ADAPTER)
    for key,item in family.items():
        if key in profile_rows and profile_rows[key]!=item:raise ValueError('W03 profile conflicts with selected predecessor: '+key)
        profile_rows[key]=item
    profile['files']=[profile_rows[key] for key in sorted(profile_rows)]
    profile['integration_members_binding']=row(NEW/'integration-members.json')
    profile['claim_ceiling']=CLAIM
    save(NEW/'contract-profile.json',profile)
    source_rows={item['path']:item for item in manifest['files'] if not item['path'].startswith(op)}
    for item in own:
        if item['path'].endswith('/contract-profile.json'): continue
        current=row(NEW/item['path'][len(op):]);source_rows[current['path']]=current
    if old_adapter_path not in source_rows:raise ValueError('API55 adapter absent from Source')
    source_rows.pop(old_adapter_path)
    source_rows[row(NEW_ADAPTER)['path']]=row(NEW_ADAPTER)
    manifest['files']=[source_rows[key] for key in sorted(source_rows)]
    manifest['profile_binding']=row(NEW/'contract-profile.json')
    manifest['predecessor_source_manifest_binding']=row(OLD/'source-manifest.json')
    manifest['claim_ceiling']=CLAIM
    save(NEW/'source-manifest.json',manifest)
    save(NEW/'rebind-receipt.json',{'schema_version':'lab-T31-API56-W03-current/v1-candidate',
        'predecessor_source_binding':row(OLD/'source-manifest.json'),
        'source_binding':row(NEW/'source-manifest.json'),'profile_binding':row(NEW/'contract-profile.json'),
        'w03_source_binding':row(FAMILY/'source/source-manifest.json'),
        'w03_context_binding':row(FAMILY/'context-w03-0005/source-manifest.json'),
        'native_disposition_constructor_binding':row(ROOT/'implementation/lab-runtime/local-host/t31-api56-w03-current-0001/native_dispositions_w03.py'),
        'selected_source_files':len(manifest['files']),'selected_profile_files':len(profile['files']),
        'actual_workflow_transitions':0,'authority_effect':'none','claim_ceiling':CLAIM})
    print(json.dumps({'source_sha256':sha(raw(NEW/'source-manifest.json')),
                      'profile_sha256':sha(raw(NEW/'contract-profile.json')),
                      'source_files':len(manifest['files']),'profile_files':len(profile['files'])},sort_keys=True))


if __name__=='__main__':main()
