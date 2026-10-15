"""Independent static review + explicitly owned inert ports; no real runtime guards."""
import ast,copy,datetime,hashlib,json,os,runpy,sys
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';P=RUN/'T32/native-node-recovery-qualification-preparation-0004';OLD=P.with_name('native-node-recovery-qualification-preparation-0003');V1=P.with_name('native-node-recovery-qualification-preparation-0001');OUT=P.with_name('native-node-recovery-qualification-independent-review-0004')
checks=[]
def need(v,label):
 if not v:raise ValueError(label)
def check(v,label):need(v,label);checks.append(label)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def obj(p):return json.loads(Path(p).read_bytes())
def binding(b):
 q=R/b['path'];check(sha(q)==b['sha256'],'exact SHA '+b['path'])
 if 'size_bytes'in b:check(q.stat().st_size==b['size_bytes'],'exact size '+b['path'])
 return q
def fdmap():
 out={}
 for v in os.listdir('/proc/self/fd'):
  try:s=os.fstat(int(v));out[v]=(s.st_dev,s.st_ino,s.st_mode)
  except OSError:pass
 return out
def shape(n):return ast.dump(n,include_attributes=False)
def defs(p):return {n.name:n for n in ast.parse(p.read_bytes()).body if isinstance(n,ast.FunctionDef)}
def case(fn):return next(n for n in ast.walk(fn)if isinstance(n,ast.With)and any(isinstance(i.context_expr,ast.Call)and isinstance(i.context_expr.func,ast.Attribute)and i.context_expr.func.attr=='signed_catalog'for i in n.items))
before=fdmap()
for name,pin in {'HANDOFF.json':'f45404133c9dd69629385d41e33cb86e4798753915b42c18063483426c464fb3','source-manifest.json':'c2750cb321001720e081f117f5e5c3afa75b398ef8a36b7072cfd52e3905c50b','qualify.py':'63d8b2687c7e2d0d79a713b7e033db0aa20e16ce1954732535c8a6c051868198','execution-selection-INACTIVE.json':'10eb22d3034193e418f7c7af007f8e9652ab8a5cbd17d2e38a5a9a0a299b2311','root-dispatch-INACTIVE.json':'b261904d08d5520b0dcb50461c88393943a469df80d66b1ad7935af9f99aca41'}.items():check(sha(P/name)==pin,'Root/author independent selected '+name)
mf=obj(P/'source-manifest.json');rows=mf['files'];check(len(rows)==382 and len({x['path']for x in rows})==367,'382 declared occurrences367 distinct origins')
for b in rows:binding(b)
packet=obj(P/'execution-selection-INACTIVE.json');dispatch=obj(P/'root-dispatch-INACTIVE.json');refs=packet['reference_bindings']
for b in refs.values():binding(b)
g=obj(R/refs['adoption_manifest']['path'])['files'];e=obj(R/refs['execution_manifest']['path'])['files'];check(len(g)==153 and len(e)==176,'exact current153 guard176 execution scopes')
# Full literal occurrence preservation, including overlap; no set-dedup claim.
for scope in (g,e):
 for b in scope:check(b in rows,'literal parent declaration '+b['path'])
from collections import Counter
key=lambda b:json.dumps(b,sort_keys=True,separators=(',',':'))
required=Counter(key(b)for b in g+e);actual=Counter(key(b)for b in rows);check(all(actual[k]>=v for k,v in required.items()),'every overlapping occurrence conserved without deduplication')
lineage=obj(P/'PREDECESSOR-LINEAGE.json');binding(lineage['prior3_manifest_binding']);check(lineage['prior3_full361_manifest']==obj(R/lineage['prior3_manifest_binding']['path']),'all361 prior metadata exact and literal');check(all(x in rows for x in lineage['prior3_full361_manifest']['files']),'all361 actual parent declarations retained');binding(lineage['actual_prior3_CAP03_attempt']);[binding(x)for x in lineage['peer3_and_erratum']]
new=defs(P/'qualify.py');old=defs(OLD/'qualify.py');v1=defs(V1/'qualify.py')
check(set(new)==set(old),'complete runner helper membership retained')
for name in old:
 if name!='run':check(shape(new[name])==shape(old[name]),'unchanged helper '+name)
check(shape(case(new['run']))==shape(case(old['run']))==shape(case(v1['run'])),'complete original four-case block exact AST across three versions')
for n in ('need','sha','parse','relative','bootstrap_capture','module','diagnostic','main'):check(shape(new[n])==shape(v1[n]),'original eight helper AST '+n)
for n in ('boundary.py','capture.py','resource-accounting-contract.json'):check((P/n).read_bytes()==(OLD/n).read_bytes(),'exact predecessor '+n)
final=lambda fn:next(n.finalbody for n in fn.body if isinstance(n,ast.Try))
check([shape(n)for n in final(new['run'])[:-1]]==[shape(n)for n in final(old['run'])[:-1]],'all independent exits/FD final acceptance before result unchanged')
for name in ('fd_snapshot','classify_initialization','verify_libffi_descriptor','runtime_initialization','operational_fd_check'):check(shape(new[name])==shape(old[name]),'strict initialization and exact FD protocol '+name)
check(packet['schema_version']=='lab-T32-owned-node-recovery-qualification/v2-candidate' and dispatch['schema_version']=='lab-T32-Root-owned-technical-dispatch/v2-candidate','explicit successor selection and dispatch versions')
check(dispatch['reference_bindings']==refs and dispatch['ontology_execution_selection_binding']==packet['ontology_execution_selection_binding'],'Root dispatch joins exact full references and actual role selector')
check(packet['root_dispatch_binding']is None and packet['technical_deadline_utc']is None and packet['store_parent']==packet['output_root']=={'path':None,'identity':None},'no fabricated active roots/deadline/Rootdispatch')
check(dispatch['store_parent']==dispatch['output_root']=={'path':None,'identity':None} and dispatch['technical_deadline_utc']is None,'inactive Root dispatch custody')
for b in packet['active_code_bindings']:binding(b)
check(len(packet['active_code_bindings'])==len({b['path']for b in packet['active_code_bindings']})==17,'exact17 unique active true-code origins')
check(packet['module_bindings']['executor']=={'path':str((RUN/'T07/ontology-native-execution-preparation-0002/native_executor.py').relative_to(R)),'sha256':'6dc340b7b533ef138963383340f6874d84950daab992126b04bd16ad17a58c9e'},'actual selected new executor6dc origin')
check(packet['ontology_execution_selection_binding']=={'path':str((RUN/'T07/ontology-installation-root-0002/execution-selection.json').relative_to(R)),'sha256':'3b67921318a8d9153f798c91d954e015bda51846608ded31cb6c8cc189806c10'},'actual installed role selector3b679')
selector=obj(binding(packet['ontology_execution_selection_binding']));check(selector['ontology_role']['sha256']=='82713671f1c1271f92b7ae675ccee531c0ee972828e25899c0c19e64015025f6','selector exact current827 role');binding(selector['installation_receipt_binding'])
for leaf,pin in [('selected_store.py','83bd3d974c2e7d8e4f7b060b9b1678f8bb796a3ffac2bc5d10f1dd58af6f3a8f'),('generation_store.py','504d5f00abc43e666027f1972cf12829491ccaf5fd5ebac3f4300a2c5f68f1f4')]:check(any(Path(b['path']).name==leaf and b['sha256']==pin for b in packet['active_code_bindings']),'selected active '+leaf)
for n in ('api_source_binding','api_profile_binding'):binding(packet[n])
check('ctypes'not in sys.modules,'no ctypes imported by static audit')
# Execute retained author47 inert checks, never their __main__ exclusive writer.
author=runpy.run_path(str(P/'controls_contract.py'),run_name='_independent_pure_control_selection')['main']();check(author['total_checks']==47 and author['FD_delta']==0 and not author['actual_API_Source_native_executor_boundary_installation_or_lease_used'],'actual retained47 inert controls PASS')
# Independently execute original dispatch/deadline validation AST on symbolic
# selected bytes only. No runtime constructors/Source/guard modules are loaded.
body=new['run'].body;start=next(i for i,n in enumerate(body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='dispatch'for t in n.targets));stop=next(i for i,n in enumerate(body[start:],start)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='mods'for t in n.targets));unit=ast.Module(body=copy.deepcopy(body[start:stop]),type_ignores=[]);ast.fix_missing_locations(unit);code=compile(unit,str(P/'qualify.py'),'exec')
p=copy.deepcopy(packet);p['root_dispatch_binding']={'path':'OWNED-FIXTURE-DISPATCH','sha256':'0'*64};p['store_parent']={'path':'/OWNED-INERT-STORE','identity':[1,2,3,448]};p['output_root']={'path':'/OWNED-INERT-OUTPUT','identity':[1,4,3,448]};p['technical_deadline_utc']=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=120)).isoformat();d=copy.deepcopy(dispatch)
for k in ('store_parent','output_root','technical_deadline_utc'):d[k]=p[k]
def exercise(label,change=None,refuse=False):
 pp,dd=copy.deepcopy(p),copy.deepcopy(d)
 if change:change(pp,dd)
 ports=[]
 def exact(row):
  ports.append(row)
  return json.dumps(dd).encode()if row==pp['root_dispatch_binding']else b'OWNED-INERT-INSTALLED-SELECTOR'
 env={'packet':pp,'exact':exact,'parse':json.loads,'need':need,'datetime':datetime,'EXECUTION':packet['ontology_execution_selection_binding']}
 try:exec(code,env)
 except (ValueError,TypeError,KeyError):check(refuse,label+' expected refusal')
 else:check(not refuse,label+' expected acceptance')
 check(all(x==pp['root_dispatch_binding']or x==packet['ontology_execution_selection_binding']for x in ports),label+' only inert selected byte ports')
exercise('matching current closed v2 dispatch')
exercise('reference substitution',lambda p,d:d['reference_bindings'].update(adoption_peer={'path':'WRONG','sha256':'0'*64}),True)
exercise('executor role substitution',lambda p,d:d['ontology_execution_selection_binding'].update(sha256='0'*64),True)
exercise('unknown dispatch field',lambda p,d:d.update(unknown=True),True)
exercise('old v1 dispatch',lambda p,d:d.update(schema_version='lab-T32-Root-owned-technical-dispatch/v1-candidate'),True)
exercise('reordered case cohort',lambda p,d:d.update(native_cases=list(reversed(d['native_cases']))),True)
exercise('deadline above900',lambda p,d:[p.update(technical_deadline_utc=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=901)).isoformat()),d.update(technical_deadline_utc=p['technical_deadline_utc'])],True)
exercise('expired deadline',lambda p,d:[p.update(technical_deadline_utc=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(seconds=1)).isoformat()),d.update(technical_deadline_utc=p['technical_deadline_utc'])],True)
exercise('nonUTC deadline',lambda p,d:[p.update(technical_deadline_utc=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=120)).astimezone(datetime.timezone(datetime.timedelta(hours=1))).isoformat()),d.update(technical_deadline_utc=p['technical_deadline_utc'])],True)
public=runpy.run_path(str(P/'controls_public.py'),run_name='_independent_public_reader_controls')['main']();check(public['check_count']==15 and public['all329_reader_domains_eligible'] and public['FD_delta']==0,'actual15 public Cargo and owned filesystem capture controls PASS')
check(len(public['declared_occurrences'])==329 and sum(x['size_bytes']>32*1024*1024 for x in public['declared_occurrences'])==1,'every329 input classified in original32MiB or exact Cargo reader domain')
# Reject all undeclared changes to run, including the caching/exit/clock code.
normalized=copy.deepcopy(new['run']);original=old['run']
new_public=next(x for x in normalized.body if isinstance(x,ast.FunctionDef)and x.name=='selected_public');check('40680304'in ast.unparse(new_public) and 'limit=cargo_size, size=cargo_size'in ast.unparse(new_public),'large reader exact independent public byte-size contract')
bootstrap=next(x for x in normalized.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='public_control'for t in x.targets));check(ast.unparse(bootstrap)=="public_control = module('_T32_public_capture_' + uuid.uuid4().hex, CONTROL, capture(CONTROL, CONTROL_SHA))",'reviewed control module bootstrapped from original captured exact true origin')
normalized.body=[x for x in normalized.body if x is not new_public and x is not bootstrap]
freshfor=lambda fn:next(x for x in ast.walk(fn)if isinstance(x,ast.For)and isinstance(x.target,ast.Name)and x.target.id=='row'and isinstance(x.iter,ast.Name)and x.iter.id=='fresh')
a,b=freshfor(normalized),freshfor(original);check(len(a.body)==4 and len(b.body)==5 and [shape(x)for x in a.body[:2]]==[shape(x)for x in b.body[:2]]and shape(a.body[3])==shape(b.body[4])and ast.unparse(a.body[2])=='raw = selected_public(row)','only full-row reader routing changed, cache and origin logic exact')
a.body=copy.deepcopy(b.body);check(shape(normalized)==shape(original),'entire run AST identical after exact declared reader adaptation normalization')
for b in rows:binding(b)
check(fdmap()==before and 'ctypes'not in sys.modules,'all static and inert checks exact FD map unchanged no ctypes')
result={'schema_version':'lab-T32-runner4-independent-controls/v1','result':'PASS-static-and-owned-inert-only','check_count':len(checks),'checks':checks,'retained_inert_checks':47,'passive_public_and_owned_FS_checks':15,'all329_reader_domains_eligible':True,'additional_dispatch_cases':9,'manifest_occurrences_entry_exit':382,'manifest_unique_origins':367,'current_runtime_scope_occurrences':329,'FD_delta':0,'Source_API_native_executor_boundary_installation_compiler_or_lease_used':False,'full_installed_or_Source_guard_used':False,'actual4cases_runtime_qualified':False,'authority_effect':'none'}
(OUT/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='checks'},sort_keys=True))
