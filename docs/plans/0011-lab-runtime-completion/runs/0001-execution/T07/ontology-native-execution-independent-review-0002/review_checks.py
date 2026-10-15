"""Independent static byte/AST/readelf audit. No candidate executor/guard imported."""
import ast,copy,hashlib,json,os,re,stat,struct,subprocess
from pathlib import Path
R=Path('/home/vlad_/projects/CyberAlchemy-lab');RUN=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution';P=RUN/'T07/ontology-native-execution-preparation-0002';OLD=P.with_name('ontology-native-execution-preparation-0001');OUT=P.with_name('ontology-native-execution-independent-review-0002')
checks=[]
def need(v,label):
 if not v:raise AssertionError(label)
 checks.append(label)
def raw(p):return Path(p).read_bytes()
def sha(p):return hashlib.sha256(raw(p)).hexdigest()
def obj(p):return json.loads(raw(p))
def check(b):
 p=R/b['path'];need(sha(p)==b['sha256'],'SHA '+b['path'])
 if 'size_bytes'in b:need(p.stat().st_size==b['size_bytes'],'size '+b['path'])
 if 'mode'in b:need(stat.S_IMODE(p.stat().st_mode)==b['mode'],'mode '+b['path'])
 return p
def fdmap():
 d={}
 for v in os.listdir('/proc/self/fd'):
  try:s=os.fstat(int(v));d[v]=(s.st_dev,s.st_ino,s.st_mode)
  except OSError:pass
 return d
def readelf(p,flag):
 x=subprocess.run(['/usr/bin/readelf','-W',flag,str(p)],env={'PATH':'/usr/bin:/bin','LC_ALL':'C'},capture_output=True,timeout=15,check=True)
 need(not x.stderr,'readelf no error '+str(p)+' '+flag);return x.stdout.decode('utf8')
before=fdmap()
pins={'HANDOFF.json':'0a99c01d9867a9161efaabc58b7107d18a711c408994b9a19a8e65f58f45fffc','source-manifest.json':'cec90b3efee6a949706bef250447db110da5d07a0bcfe88eae082be061eb7548','native_executor.py':'6dc340b7b533ef138963383340f6874d84950daab992126b04bd16ad17a58c9e','ROOT-PREPARE-PROVISION-PROPOSAL.json':'b506322170257a5b44388ac0fa77bbed9302bc05f7e08f14a1f003ec8fe237b5'}
for name,pin in pins.items():need(sha(P/name)==pin,'independent selected '+name)
mf=obj(P/'source-manifest.json');need(len(mf['files'])==176,'176 selected declarations')
for b in mf['files']:check(b)
parent=obj(OLD/'source-manifest.json');need(len(parent['files'])==19,'19 original declarations');need(all(x in mf['files'] for x in parent['files']),'all19 parent rows literal preserved')
rust=obj(RUN/'T32/native-rust-provenance-preparation-0001/input-selection.json');need(len(rust['files'])==110,'110 Rust inputs');need(all(x in mf['files'] for x in rust['files']),'all110 Rust input rows literal preserved')
old=ast.parse(raw(OLD/'native_executor.py'));new=ast.parse(raw(P/'native_executor.py'));n=copy.deepcopy(new);changes=[]
for node in n.body:
 if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('VERSION','ONTOLOGY_SHA'):
  k=node.targets[0].id;prior=next(x for x in old.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id==k)
  changes.append({'constant':k,'old':ast.literal_eval(prior.value),'new':ast.literal_eval(node.value)});node.value=copy.deepcopy(prior.value)
need(len(changes)==2,'only two selected constant declarations');need(ast.dump(old,include_attributes=False)==ast.dump(n,include_attributes=False),'entire module AST identical after two literals normalized')
need(sum(isinstance(x,ast.FunctionDef)for x in ast.walk(old))==23,'all23 function and nested bodies unchanged')
direct=sum(isinstance(x,ast.FunctionDef)for x in old.body)+sum(isinstance(m,ast.FunctionDef)for x in old.body if isinstance(x,ast.ClassDef)for m in x.body);need(direct==19,'all19 direct function/method bodies unchanged')
values={x.targets[0].id:ast.literal_eval(x.value)for x in new.body if isinstance(x,ast.Assign)and isinstance(x.targets[0],ast.Name)and isinstance(x.value,ast.Constant)}
need(values['VERSION']=='lab-ontology-native-execution-selection/v2-candidate' and values['ONTOLOGY_SHA']=='82713671f1c1271f92b7ae675ccee531c0ee972828e25899c0c19e64015025f6','exact new role version and byte SHA')
lineage=obj(P/'SOURCE-BUILD-LINEAGE.json');terminal_path=check(lineage['Root_actual_archival_terminal_binding']);terminal=obj(terminal_path);result_path=check(terminal['result_binding']);result=obj(result_path)
need(terminal['exit_code']==0 and terminal['session_id']==40068 and terminal['actual_result']==result,'Root actual command terminal40068 exit0 exact result')
need(len(terminal['retained_raw'])==22,'22 archived raw observations')
for row in terminal['retained_raw']:
 q=check(row['retained_copy']);need(raw(q)==raw(row['actual_origin']),'raw copy exact actual '+q.name)
need(len(result['commands'])==5 and all(x['returncode']==0 and x['failure']is None and not x['timed_out'] and x['owned_group_gone'] and not x['cleanup_errors'] and not x['stream_errors'] for x in result['commands']),'all five actual command statuses and owned child cleanup')
need(not result['exit_errors'] and not result['unexecuted_command_ids'],'no recorded guard exit errors or unexecuted command')
prod=R/'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001/production';names=[]
for q in sorted((prod/'tests').glob('*.rs')):names+=re.findall(r'#\[test\]\s*fn\s+(\w+)\s*\(',q.read_text())
stdout=raw(next(x for x in result['commands'] if x['id']=='04-original23-regressions')['stdout']['path']).decode();observed=re.findall(r'^test ([A-Za-z0-9_]+) \.\.\. (ok|FAILED|ignored)$',stdout,re.M)
need(len(names)==23 and len(set(names))==23 and sorted(observed)==sorted((v,'ok')for v in names),'all actual23 names and outcomes directly match current original test source')
for row in result['commands']:
 check(row['stdout']);check(row['stderr'])
binaries=[]
for label in ('03-fresh-build','05-independent-target-build'):
 b=result['accepted_observations'][label];q=check({'path':b['path'],'sha256':values['ONTOLOGY_SHA'],'size_bytes':20843752,'mode':493});binaries.append(raw(q));need(b['artifact']['fresh']is False and b['artifact']['target']['src_path']==str(prod/'src/main.rs'),'fresh actual Cargo compile of exact original main '+label)
archive=check(terminal['archived_binary']);need(raw(archive)==binaries[0]==binaries[1],'complete two build bodies and archived827 exactly equal')
need(sha(check(lineage['retained_old574_binding']))!=values['ONTOLOGY_SHA'],'574 retained distinct original bytes')
passive=obj(P/'passive-result.json');need(len(passive['matched_versioned_import_symbols'])==82,'82 reported versioned imports');need(len(passive['selected_original_ABI_provider_bindings'])==3,'three explicitly selected providers')
imports=readelf(archive,'--dyn-syms');need(len(re.findall(r'\bUND\s+\S+@',imports))==82,'independent readelf confirms82 versioned undefined symbols')
exports={}
for p in passive['selected_original_ABI_provider_bindings']:
 q=check(p);table=readelf(q,'--dyn-syms');exports[q.name]=table
for row in passive['matched_versioned_import_symbols']:
 symbol=row['name']+'@'+row['version'];need(symbol in imports,'readelf exact import '+symbol)
 pattern=r'\b'+re.escape(row['name'])+r'@{1,2}'+re.escape(row['version'])+r'(?:\s|$)';need(re.search(pattern,exports[row['provider']]) is not None,'readelf selected export '+row['provider']+' '+symbol)
meta=readelf(archive,'--file-header');need('ELF64'in meta and "2's complement, little endian"in meta and 'Advanced Micro Devices X86-64'in meta,'independent ELF architecture metadata')
dynamic=readelf(archive,'--dynamic');needed=re.findall(r'\(NEEDED\).*\[([^\]]+)\]',dynamic);need(sorted(needed)==['ld-linux-x86-64.so.2','libc.so.6','libgcc_s.so.1'],'independent ELF three needed providers')
proposal=obj(P/'ROOT-PREPARE-PROVISION-PROPOSAL.json');template=obj(P/'execution-selection-INACTIVE.json');need(proposal['new_anchor']is None and proposal['actual_installation_receipt_binding']is None and proposal['actual_role_selector_binding']is None and proposal['root_dispatch_binding']is None,'proposal actual identity/receipt/selector/dispatch null')
need(template['new_installation']is None and template['installation_receipt_binding']is None,'inactive template lacks activation custody/receipt')
need(proposal['module_bindings']==template['module_bindings'],'same explicit actual dependency/control sources');[check(b)for b in proposal['module_bindings'].values()]
need(proposal['added_sources']==[{'source_binding':{'path':str(archive.relative_to(R)),'sha256':values['ONTOLOGY_SHA']},'destination':'bin/lab-ontology-native','kind':'ontology-native-executable'}] and proposal['additional_ABI_sources']==[],'one exact archived827 additional source and no extra ABI')
base=obj(check(proposal['base_dependency_selection_binding']));need(len(base['inputs'])==720 and len(base['elf_graph'])==77,'original720 inputs and77ELF graph unchanged');need(all('lib/abi/'+s in base['elf_graph']for s in needed),'all new direct providers within selected original graph')
expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':493 if r['kind']in {'interpreter','native-executable'} else 420}for r in base['inputs']};expected.update(base['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=493;need(len(expected)==1010 and 'bin/lab-ontology-native'not in expected,'original1010 unchanged plus distinct1011th role')
need(proposal['base_anchor']==template['base_installation'],'exact explicit base anchor');s=Path(proposal['base_anchor']['path']).stat();need([s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==[proposal['base_anchor'][k]for k in ['device','inode','uid','mode']],'base anchor actual metadata matches without guard')
for b in mf['files']:check(b)
need(fdmap()==before,'exact descriptor map unchanged')
result={'schema_version':'lab-827-independent-review-controls/v1','result':'PASS-passive-byte-AST-build-evidence-review','checks':checks,'check_count':len(checks),'selected_rows_entry_exit':176,'literal_parent_rows':19,'literal_Rust_rows':110,'direct_bodies_unchanged':19,'total_bodies_unchanged':23,'actual_Root_tests_directly_accounted':23,'actual_Root_raw_artifacts_checked':22,'full_binary_bodies_equal':3,'independent_readelf_providers':3,'independent_readelf_versioned_imports':82,'FD_delta':0,'candidate_executor_imported_or_executed':False,'Source_API_native_compiler_installer_or_lease_executed':False,'full_dependency_guard_executed':False,'authority_effect':'none'}
(OUT/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='checks'},sort_keys=True))
