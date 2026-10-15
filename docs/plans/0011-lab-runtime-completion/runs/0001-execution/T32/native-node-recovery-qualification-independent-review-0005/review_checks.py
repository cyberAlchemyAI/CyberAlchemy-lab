"""Independent runner5 static / owned-inert review, no runtime imports."""
import ast, copy, hashlib, json, os
from collections import Counter
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent
C=HERE.parent/'native-node-recovery-qualification-preparation-0005'
P=HERE.parent/'native-node-recovery-qualification-preparation-0004'
checks=[]
def need(v,s):
    if not v:raise ValueError(s)
def ck(v,s):need(v,s);checks.append(s)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def bindread(row):
    p=Path(row['path']);p=p if p.is_absolute()else ROOT/p
    raw=p.read_bytes();ck(sha(raw)==row['sha256'],'sha '+str(p))
    if 'size_bytes'in row:ck(len(raw)==row['size_bytes'],'size '+str(p))
    return raw
def fdmap():
    out={}
    for name in os.listdir('/proc/self/fd'):
        try:s=os.fstat(int(name));out[name]=(s.st_dev,s.st_ino,s.st_mode)
        except OSError:continue
    return out
baseline=fdmap()
ck(sha((C/'HANDOFF.json').read_bytes())=='818357a4cf18304e7021ea1e2cac753453c24a45d32eef3544f4f65723d93f0f','exact HH5')
ck(sha((C/'source-manifest.json').read_bytes())=='7683b86c1c9bde5f1d2f09f889bc3e2ba925e164eaf36bd9ec331b457569b4e5','exact MF5')
hh=load(C/'HANDOFF.json');manifest=load(C/'source-manifest.json');original=load(P/'source-manifest.json')
ck(len(manifest['files'])==403 and len({r['path']for r in manifest['files']})==388,'403 occurrences388 physical paths')
for row in manifest['files']:bindread(row)
lineage=load(C/'PREDECESSOR-LINEAGE.json')
ck(lineage['original382_historical_rows']==original['files'],'all382 exact literal parent declarations')
missing='/tmp/cal-T32-rust-provenance-root-0001/observations/result.json'
rows=[r for r in original['files']if r['path']!=missing]
ck(len(rows)==381 and all(r in manifest['files']for r in rows),'all381 physically readable parent occurrences conserved')
ck(not (Counter(json.dumps(r,sort_keys=True)for r in rows)-Counter(json.dumps(r,sort_keys=True)for r in manifest['files'])),'parent381 literal occurrence multiplicity conserved')
ck(not Path(missing).exists(),'old missing result path remains absent')
for name in ('boundary.py','capture.py','resource-accounting-contract.json','controls_fd.py','controls_public.py'):
    ck((C/name).read_bytes()==(P/name).read_bytes(),'unchanged original '+name)
tree=ast.parse((C/'qualify.py').read_bytes());old=ast.parse((P/'qualify.py').read_bytes())
shape=lambda n:ast.dump(n,include_attributes=False)
fs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)};oldfs={n.name:n for n in old.body if isinstance(n,ast.FunctionDef)}
ck(set(fs)==set(oldfs),'all original top-level helpers retained')
ck(len(fs)==14 and all(shape(fs[k])==shape(oldfs[k])for k in fs if k!='run'),'13 exact helper ASTs')
def caseblock(run):return next(n for n in ast.walk(run)if isinstance(n,ast.With)and any('signed_catalog'in ast.unparse(i.context_expr)for i in n.items))
ck(shape(caseblock(fs['run']))==shape(caseblock(oldfs['run'])),'all original four case block AST unchanged')
def final(run):return next(n.finalbody for n in run.body if isinstance(n,ast.Try)and n.finalbody)
ck([shape(n)for n in final(fs['run'])]==[shape(n)for n in final(oldfs['run'])],'whole outer finally unchanged')
packet=load(C/'execution-selection-INACTIVE.json');dispatch=load(C/'root-dispatch-INACTIVE.json');oldpacket=load(P/'execution-selection-INACTIVE.json')
ck(packet['technical_deadline_utc']is packet['root_dispatch_binding']is None and packet['store_parent']==packet['output_root']=={'path':None,'identity':None},'owned roots/deadline/dispatch inactive')
ck(packet['schema_version']=='lab-T32-owned-node-recovery-qualification/v3-candidate'and dispatch['schema_version']=='lab-T32-Root-owned-technical-dispatch/v3-candidate','explicit successor contracts v3')
ck(packet['reference_bindings']==dispatch['reference_bindings']and len(packet['reference_bindings'])==8,'all eight dispatch refs join')
for name in set(oldpacket)-{'schema_version','active_code_bindings','owned_code_bindings','root_dispatch_binding','reference_bindings'}:
    ck(packet[name]==oldpacket[name],'unchanged original packet field '+name)
active=packet['active_code_bindings'];ck(len(active)==len({r['path']for r in active})==17,'all active17 distinct')
for r in active:bindread(r)
refs=packet['reference_bindings'];metadata={k:json.loads(bindread(r))for k,r in refs.items()}
hist=metadata['execution_manifest']['files'];current=metadata['execution_current_manifest']['files'];locator=metadata['execution_occurrence_map']
ck(len(hist)==176 and len(current)==175 and len({r['path']for r in current})==175,'176 historical175 physical')
ck(current==[r for i,r in enumerate(hist)if i!=82]and hist[82]['path']==missing,'sole exact historical row82 unavailable')
archive=locator['archive_binding']['path'];ck(hist[131]['path']==archive and hist[82]['sha256']==hist[131]['sha256']=='b126e629fc314325391dffcf3a93609196ad6218e6efaf54ff4e98ffaae0fe5a','archive exact original result content identity')
for r in current:bindread(r)
ck([v['historical_index']for v in locator['occurrences']]==list(range(176)),'all176 historical indices ordered exactly')
ck(all(v['historical_row']==hist[i]for i,v in enumerate(locator['occurrences'])),'all176 literal original rows retained in map')
ck(len({v['current_index']for v in locator['occurrences']})==175 and sum(current[v['current_index']]['path']==archive for v in locator['occurrences'])==2,'two archive occurrences retain175 physical scope')
nested={n.name:n for n in fs['run'].body if isinstance(n,ast.FunctionDef)}
selectednodes=[copy.deepcopy(nested[k])for k in ('execution_occurrences','all_selected')]
inert=ast.Module(body=selectednodes,type_ignores=[]);ast.fix_missing_locations(inert)
trace=[];reads=[];mut={};failpath=None
def exact(row):
    role=next((k for k,v in refs.items()if row==v),None)
    if role is None:return b'independent-inert-owned-code'
    reads.append(role);return json.dumps(mut.get(role,metadata[role])).encode()
def selected_public(row):
    trace.append((row['path'],row['sha256']))
    if row['path']==failpath:raise ValueError('independent injected read refusal')
    return b'independent-inert-selected-body'
scope={'Path':Path,'ROOT':ROOT,'need':need,'parse':json.loads,'exact':exact,'refs':refs,'selected':metadata['adoption_manifest']['files'],'execution_selected':hist,'selected_cache':{},'selected_public':selected_public,'own':packet['owned_code_bindings'],'packet_binding':{'path':'independent-owned-packet','sha256':'0'*64},'packet':packet}
exec(compile(inert,str(C/'qualify.py'),'exec'),scope)
occurrence=scope['execution_occurrences'];proof=scope['all_selected']
ck(len(occurrence())==176,'extracted real occurrence function positive')
proof();first=list(trace);trace.clear();proof();ck(trace==first and len(trace)==329,'second proof recaptures every329 occurrence without proof cache')
ck(sum(p==archive for p,_ in trace)==2 and not any(p==missing for p,_ in trace),'each proof reads archive twice and never claims old path')
ck(all(reads.count(k)>=2 for k in refs),'all eight metadata refs freshly read on repeated proofs')
def refuse(role,change,label):
    original_fds=fdmap();value=copy.deepcopy(metadata[role]);change(value);mut[role]=value
    try:
        try:occurrence()
        except (ValueError,KeyError,TypeError,IndexError):checks.append(label)
        else:raise AssertionError('accepted invalid '+label)
    finally:mut.clear()
    ck(fdmap()==original_fds,'FD conserved '+label)
refuse('execution_manifest',lambda x:x['files'].pop(82),'historical declaration deletion refused')
refuse('execution_current_manifest',lambda x:x['files'].pop(131),'current input deletion refused')
refuse('execution_current_manifest',lambda x:x['files'].__setitem__(0,x['files'][1]),'current input duplicate refused')
refuse('execution_current_manifest',lambda x:x.update(historical_missing_path_restored=True),'historical path restoration claim refused')
refuse('execution_occurrence_map',lambda x:x['occurrences'].__setitem__(82,x['occurrences'][131]),'lost historical index refused')
refuse('execution_occurrence_map',lambda x:x['occurrences'][82].update(current_index=0),'wrong physical content locator refused')
refuse('execution_occurrence_map',lambda x:x.update(archive_captures_each_all_selected_call=1),'duplicate proof occurrence suppression refused')
refuse('execution_occurrence_map',lambda x:x.update(old_path_restored_or_alias_equivalence_claimed=True),'old path equivalence refused')
refuse('execution_occurrence_map',lambda x:x.update(cross_call_cache_allowed=True),'cross call proof cache refused')
refuse('execution_current_handoff',lambda x:x['occurrence_map_binding'].update(sha256='0'*64),'provenance map substitution refused')
for position in (0,82,175):
    failpath=occurrence()[position]['path']
    try:proof()
    except ValueError:checks.append('fresh row refusal reaches outer proof at historical index '+str(position))
    else:raise AssertionError('fresh row refusal suppressed')
    finally:failpath=None
for row in manifest['files']:bindread(row)
ck(fdmap()==baseline,'exact FD map unchanged at exit')
result={'result':'PASS-scoped-inactive-runner5','check_count':len(checks),'checks':checks,'FD_delta':0,'actual_runtime_Source_guard_native_compiler_lease_used':False,'inert_ports_only':True}
(HERE/'checks-result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='checks'}))
