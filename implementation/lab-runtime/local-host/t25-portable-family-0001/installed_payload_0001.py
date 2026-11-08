"""Pinned historical locator data and actual installed payload are separate.

No historical input locator is opened. The independently captured original
selection, declared package payload, and actual fresh installed files must
agree. Original source-input validators remain unchanged historical inputs.
"""
import cal_installed_runtime_selection_v1 as P
P.guard()
import hashlib,json,os,re,stat
from pathlib import Path,PurePosixPath
SELECTION={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json','sha256':'2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'}
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
FIELDS=set('schema_version authority_effect actual_owner_outcome environment execution_configuration versions inputs elf_graph wheel_members wheel_elf_bindings inspection_tool original_bindings excluded_stdlib_inputs original_full_proof excluded_protected_inputs supported_scope old_disposable_locators'.split())
def need(value,reason):
 if not value:raise ValueError(reason)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def historical_locators(selection):
 """Validate recorded original provenance lexically; never follow old paths."""
 rows=selection['inputs'];wheels=[row for row in rows if row['kind']=='wheel']
 need(len(wheels)==8,'original eight wheel locators required')
 suffix=PurePosixPath('product/lab/release-candidates/v1/packaging/R02/packages/0003/wheels').parts
 parent=PurePosixPath(wheels[0]['path']).parent
 need(parent.is_absolute() and parent.parts[-len(suffix):]==suffix,'recorded original wheel source differs')
 origin=PurePosixPath(*parent.parts[:-len(suffix)])
 v1=origin/'product/lab/release-candidates/v1/interface/runtime-dependencies-v1-completion-0001/installations/0001'
 destinations=set()
 for row in rows:
  kind=row['kind'];need(kind in {'wheel','interpreter','native-executable','stdlib','host-abi'},'unknown recorded dependency kind')
  need(set(row)==set('kind path sha256 size_bytes mode destination classification'.split())|({'soname'}if kind=='host-abi'else set()),'closed recorded dependency row required')
  path=PurePosixPath(row['path']);destination=PurePosixPath(row['destination'])
  need(path.is_absolute() and path.as_posix()==row['path'] and '..'not in path.parts and '\\'not in row['path'] and '\0'not in row['path'],'canonical recorded source locator required')
  need(not destination.is_absolute() and destination.as_posix()==row['destination'] and '..'not in destination.parts and row['destination']not in destinations,'unique installed relative destination required');destinations.add(row['destination'])
  need(type(row['sha256'])is str and re.fullmatch('[a-f0-9]{64}',row['sha256']) and type(row['size_bytes'])is int and row['size_bytes']>=0 and type(row['mode'])is int and 0<=row['mode']<=0o777,'recorded digest/size/mode differs')
  need(path.suffix not in {'.key','.pem','.pyc'} and not any(part=='.env'or part.startswith('.env.')for part in path.parts),'protected/cache locator outside public dependency closure')
  need(row['classification']==('host-dependency-public-system-bytes'if kind=='host-abi'else'public-installation-bytes'),'recorded disclosure class differs')
  if kind=='wheel':need(path.parent==origin/PurePosixPath(*suffix) and row['destination']=='wheels/'+path.name,'original wheel provenance differs')
  elif kind=='stdlib':need(path.is_relative_to('/usr/lib/python3.14')and row['destination']=='lib/python3.14/'+path.relative_to('/usr/lib/python3.14').as_posix(),'recorded stdlib provenance differs')
  elif kind=='host-abi':need(path.parent==PurePosixPath('/usr/lib/x86_64-linux-gnu')and '/'not in row['soname']and row['destination']=='lib/abi/'+row['soname'],'recorded ABI provenance differs')
  else:need(path==v1/'bin'/('python'if kind=='interpreter'else'lab-context-native-reader')and row['destination']=='bin/'+path.name and row['mode']==0o755,'recorded execution provenance differs')
 for row in selection['wheel_elf_bindings']:
  need(set(row)==set('path sha256 size_bytes mode destination'.split())and PurePosixPath(row['path'])==v1/row['destination']and row['destination']in selection['wheel_members']and {key:row[key]for key in ('sha256','size_bytes','mode')}==selection['wheel_members'][row['destination']],'recorded wheel ELF provenance differs')
 return {'historical_source_locators_opened':False,'recorded_source_origin':str(origin)}
def selected_payload(selection,dependencies):
 package=P.current().package;declared=package['native_payload']
 need(dict(declared['selection_binding'])==SELECTION,'independently selected original payload binding differs')
 expected=dependencies.BASE.installed_files(selection)
 members={name:dict(row)for name,row in declared['members'].items()}
 need(len(expected)==len(members)==1010 and expected==members,'original selected destinations and independently packaged payload differ')
 return members
def load_selection(path,pin,dependencies,control):
 P.guard();need(Path(path)==P.root()/SELECTION['path']and pin==SELECTION['sha256'],'exact historical selection required')
 raw=control.capture(Path(path),pin);need(digest(raw)==SELECTION['sha256'],'original selection bytes differ')
 selection=dependencies.BASE.IO.parse(raw)
 need(type(selection)is dict and set(selection)==FIELDS and selection['schema_version']=='lab-runtime-dependency-closure/v2-candidate'and selection['authority_effect']=='none'and selection['actual_owner_outcome']is None,'closed historical dependency selection required')
 need(len(selection['inputs'])==720 and len(selection['elf_graph'])==77,'whole original720/77 dependency selection required')
 historical_locators(selection)
 need({row['path']:row['sha256']for row in selection['original_bindings']}==dependencies.EXPECTED_BINDINGS,'complete original proof declarations differ')
 for row in selection['original_bindings']:control.capture(P.root()/row['path'],row['sha256'])
 selected_payload(selection,dependencies);P.guard();return selection,raw
def verify_installed(destination,selection,dependencies,control):
 P.guard();root=Path(destination);need(root==Path(P.value('native.root')),'actual selected installed root differs')
 members=selected_payload(selection,dependencies)
 # BASE.verify_installed checks all1010 actual bytes, sizes, modes, ancestry,
 # owner and exact inventory. Its historical strict_structure wrapper is not
 # an installed-file predicate and is intentionally kept out of this path.
 expected=dependencies.BASE.verify_installed(root,selection)
 need(expected==members,'actual installed payload declaration differs')
 row=P.value('native.receipt');raw=control.capture(root/'installation.json',row['sha256'],owner=os.getuid(),mode=0o600)
 receipt=json.loads(raw);s=root.lstat();identity=[s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]
 need(set(receipt)==set('schema identity selection_sha256 file_count payload_manifest_sha256'.split())and receipt['schema']=='cal-clean-installed-native-runtime/v1'and receipt['identity']==identity==P.value('native.identity')and receipt['selection_sha256']==SELECTION['sha256']and receipt['file_count']==1010 and receipt['payload_manifest_sha256']==digest(encoded(members)),'actual fresh installation receipt differs')
 for name,graph in selection['elf_graph'].items():need(dependencies.BASE.elf(root/name)==graph,'actual installed ELF graph differs')
 need(members['bin/lab-context-native-reader']['sha256']==NATIVE_SHA,'actual original Context executable differs')
 P.guard();return expected
