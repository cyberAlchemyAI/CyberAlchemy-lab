"""Owned metadata closure builder. No Lab imports, effects or callback changes."""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import stat

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
API='product/lab/release-candidates/v1/interface/api-integration-v17/'

def need(value,reason):
    if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def parse(raw):
    def pairs(rows):
        result={}
        for key,value in rows:
            need(key not in result,'duplicate metadata field');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs)

def capture(row):
    name=row['path'];relative=Path(name)
    need(type(name)is str and not relative.is_absolute() and '..' not in relative.parts and relative.as_posix()==name,'true canonical relative path')
    path=ROOT/relative;held=[os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)]
    try:
        for part in path.parts[1:-1]:held.append(os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=held[-1]))
        held.append(os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=held[-1]))
        before=os.fstat(held[-1]);need(stat.S_ISREG(before.st_mode),'regular selected public file')
        chunks=[]
        while block:=os.read(held[-1],1024*1024):chunks.append(block)
        raw=b''.join(chunks)
        stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        need(stamp(before)==stamp(os.fstat(held[-1])) and sha(raw)==row['sha256'],'exact selected bytes')
        need('size_bytes' not in row or len(raw)==row['size_bytes'],'exact declared size')
        for index,part in enumerate(path.parts[1:]):
            a=os.stat(part,dir_fd=held[index],follow_symlinks=False);b=os.fstat(held[index+1])
            need((a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid)==(b.st_dev,b.st_ino,b.st_mode,b.st_uid,b.st_gid),'held full no-follow attachment')
        return raw,{'path':name,'sha256':row['sha256'],'size_bytes':len(raw),'mode':stat.S_IMODE(before.st_mode),'device':before.st_dev,'inode':before.st_ino}
    finally:
        for fd in reversed(held):os.close(fd)

def declaration_map(original,replacements):
    need(len(original)==294 and len({r['path'] for r in original})==294,'all294 original declarations')
    expected={API+n for n in ['current_context_sessions.py','service.py','source_bridge.py','workspace.py']}
    need(len(replacements)==4 and {r['original_declaration']['path'] for r in replacements}==expected,'exact four historical substitutions')
    lookup={r['original_declaration']['path']:r for r in replacements};table={r['path']:r for r in original};mapped=[]
    for position,row in enumerate(original,1):
        replacement=lookup.get(row['path']);physical=row if replacement is None else replacement['retained_binding']
        if replacement:
            need(replacement['original_declaration']==row,'original declaration identity retained')
            need(physical['path'] in table and table[physical['path']]==physical,'existing true historical buffer already selected')
            need(physical['sha256']==row['sha256'] and physical['size_bytes']==row['size_bytes'],'no old hash reinterpretation')
            need(replacement['Root_reviewed_preserved_preimage']['sha256']==row['sha256'] and replacement['Root_reviewed_preserved_preimage']['size_bytes']==row['size_bytes'],'independent reviewed preimage evidence')
        mapped.append({'position':position,'original_declaration':row,'physical_binding':physical,
            'disposition':'historical-live-locator-to-existing-true-preimage' if replacement else 'unchanged-original-physical-binding',
            'original_origin_identity_preserved':True,'old_identity_is_not_new_code_origin':True})
    need(len({r['physical_binding']['path'] for r in mapped})==290,'only exact same byte/path dedup')
    return mapped

def current_api(predecessor,margin,selectors):
    rows={r['path']:r for r in predecessor['api_expected_files']}
    need(len(rows)==160,'original capture3 API160')
    need(len(margin['actual_target_bindings'])==8,'reviewed margin8 targets')
    rows.update({r['path']:r for r in margin['actual_target_bindings']})
    need(len(selectors['rows'])==5 and sum(r['changed'] for r in selectors['rows'])==4,'reviewed selectors4 changes+1 unchanged')
    for row in selectors['rows']:
        need(row['target'] in rows and rows[row['target']]['sha256']==row['preimage']['sha256'],'selector exact original predecessor')
        rows[row['target']]=row['actual']
    need(len(rows)==165 and all(p.startswith(API) for p in rows),'all165 current API declarations')
    return [rows[name] for name in sorted(rows)]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--selection-sha256',required=True);args=parser.parse_args()
    fd_start=len(os.listdir('/proc/self/fd'));checks=[];bodies={};entry={};selected={}
    def check(name,value):need(value,name);checks.append(name)
    def read(row):
        name=row['path']
        if name in selected:need(selected[name]['sha256']==row['sha256'],'conflicting active physical selection');return bodies[name]
        raw,record=capture(row);selected[name]={'path':name,'sha256':row['sha256'],'size_bytes':len(raw)};bodies[name]=raw;entry[name]=record;return raw
    binding={'path':str((HERE/'source-selection.json').relative_to(ROOT)),'sha256':args.selection_sha256};selection=parse(read(binding));B=selection['bindings']
    inputs={name:parse(read(row)) for name,row in B.items() if not row['path'].endswith('.py')}
    original=inputs['original_margin_manifest']['files'];mapped=declaration_map(original,selection['historical_replacements'])
    for row in mapped:read(row['physical_binding'])
    for item in selection['historical_replacements']:
        check('same actual held old bytes:'+item['original_declaration']['path'],read(item['retained_binding'])==read(item['Root_reviewed_preserved_preimage']))
    api=current_api(inputs['capture3_retained_selection'],inputs['margin_application_receipt'],inputs['selector_application_receipt'])
    for row in api:read(row)
    for name,row in B.items():read(row)
    check('explicit raw294 historical metadata retained',len(original)==294 and B['original_margin_manifest']['sha256']=='d727dcd3042afeb253497cbec070ae67400269e3cf29d8e10dc005a3b4018b30')
    check('all294 ordered original identities preserved',all(row['position']==i+1 and row['original_declaration']==original[i] for i,row in enumerate(mapped)))
    check('exact290 unchanged true physical rows',len({r['physical_binding']['path'] for r in mapped})==290)
    driver_margin=[r for r in inputs['driver4_manifest']['files'] if '/observed-margin-adapter-0003/' in r['path']]
    check('driver4 consumes HH peer composition rather than stale294 table', {r['path'] for r in driver_margin}=={B[k]['path'] for k in ['original_margin_handoff','original_margin_peer','margin_composition']})
    for row in driver_margin:read(row)
    for label,raw in [('driver4',read(B['driver4_code'])),('composition',read(B['margin_composition'])),('current-runtime-margin',bodies[API+'observed_margin.py'])]:
        tree=ast.parse(raw);strings=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        check('consumer has no literal original stale margin manifest locator:'+label,not any(B['original_margin_manifest']['path'] in s for s in strings))
    check('original guard current bytes unchanged',next(r['sha256'] for r in api if r['path']==API+'guard.py')=='65ba71adb3b885f6fedc268be29f982f1f03139265f00a7e9ed08ff19b6adeb3')
    check('currentsoftware16 current API/direct bytes all selected',len(inputs['current_software_inventory']['files'])==16)
    for row in inputs['current_software_inventory']['files']:read(row)
    for item in selection['historical_replacements']:
        check('old live identity distinct from actual current body:'+item['original_declaration']['path'],selected[item['original_declaration']['path']]['sha256']!=item['original_declaration']['sha256'])
    for scenario in ['missing','wrong-original','alias-retained','wrong-hash','missing294']:
        altered=copy.deepcopy(selection['historical_replacements']);old=copy.deepcopy(original)
        if scenario=='missing':altered.pop()
        if scenario=='wrong-original':altered[0]['original_declaration']['sha256']='f'*64
        if scenario=='alias-retained':altered[0]['retained_binding']['path']=altered[0]['original_declaration']['path']
        if scenario=='wrong-hash':altered[0]['retained_binding']['sha256']='f'*64
        if scenario=='missing294':old.pop()
        try:declaration_map(old,altered)
        except ValueError:check('negative declaration mapping refuses:'+scenario,True)
        else:raise AssertionError(scenario)
    own_code={'path':str(Path(__file__).absolute().relative_to(ROOT)),'sha256':sha(Path(__file__).read_bytes())};read(own_code)
    exit_rows={name:capture(row)[1] for name,row in selected.items()};check('full actual active physical entry exit equal',entry==exit_rows)
    check('FD delta zero',len(os.listdir('/proc/self/fd'))==fd_start)
    mapping={'schema_version':'lab-T03-margin294-declaration-mapping/v1-candidate','original_manifest_binding':B['original_margin_manifest'],'rows':mapped,'all_original_declarations':294,'mapped_unique_physical_files':290,'historical_live_declarations':4,'new_original_identity_aliases':False,'authority_effect':'none','task_complete':False}
    current={'schema_version':'lab-T03-current-API165-capture-expectations/v1-candidate','files':api,'predecessor_binding':B['capture3_retained_selection'],'margin8_receipt':B['margin_application_receipt'],'selector4_receipt':B['selector_application_receipt'],'current_guard_callback_changed':False,'authority_effect':'none','task_complete':False}
    boundary={'schema_version':'lab-T03-margin-consumed-boundary-audit/v1-candidate','driver4_margin_rows':driver_margin,'current_runtime_margin_binding':selected[API+'observed_margin.py'],'current_software_inventory':B['current_software_inventory'],'original294_manifest_role':'Historical raw metadata retained. This prepared selection uses currentsoftware16 and captured composition; it does not select raw294 as a runtime software table. Future protected config must bind the exact current inventory.','runtime_source_guards':'Unchanged actual API Source/profile/configuration/fulltable guards; this new candidate metadata does not replace their callbacks.','old4_lookup':'exact original declarations in explicit mapping, true held original preimages only; actual current165 captured separately','negative_current_guard_native_or_lease_runs':False,'authority_effect':'none','task_complete':False}
    validation={'schema_version':'lab-T03-margin-final-closure-author-validation/v1-candidate','result':'PASS','checks':checks,'check_count':len(checks),'entry':list(entry.values()),'exit':list(exit_rows.values()),'FD_delta':0,'all294_declarations':294,'current_API165':165,'native_or_runtime_or_lease':False,'authority_effect':'none','task_complete':False}
    for name,value in [('declaration-map.json',mapping),('current-api-expectations.json',current),('consumed-boundary.json',boundary),('VALIDATION.json',validation),('captured-inputs.json',{'files':list(selected.values()),'authority_effect':'none'})]:
        with (HERE/name).open('xb') as f:f.write(encoded(value))
    print(json.dumps({'result':'PASS-owned-provenance-closure-preparation','checks':len(checks),'physical_rows':len(selected),'original_declarations':294,'mapped_historical_physical_rows':290,'current_API_rows':165,'FD_delta':0,'runtime_or_native_or_lease':False,'task_complete':False}))

if __name__=='__main__':main()
