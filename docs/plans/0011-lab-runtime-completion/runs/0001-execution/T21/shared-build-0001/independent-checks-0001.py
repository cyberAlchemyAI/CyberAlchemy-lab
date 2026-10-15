"""Read-only independent audit of exact Root documentation receipts and effects."""
import hashlib,json,os,stat,zipfile
from pathlib import Path,PurePosixPath
from urllib.parse import urlsplit,unquote
from markdown_it import MarkdownIt
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN='docs/plans/0011-lab-runtime-completion/runs/0001-execution/'
T=RUN+'T21/'
checks=0
bindings=[]
summary={}
def ck(ok,message):
 global checks
 checks+=1
 if not ok:raise AssertionError(message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def safe(rel):
 p=PurePosixPath(rel)
 ck(isinstance(rel,str) and str(p)==rel and not p.is_absolute() and all(x not in ('..','.') for x in p.parts),'noncanonical '+str(rel))
 q=ROOT
 for part in p.parts:
  q=q/part
  ck(not q.is_symlink(),'symlink '+str(q))
 return q
def read(rel):return safe(rel).read_bytes()
def pin(rel,sha):
 raw=read(rel);ck(digest(raw)==sha,'pin '+rel);bindings.append({'path':rel,'sha256':sha});return raw
def obj(rel,sha=None):return json.loads(pin(rel,sha) if sha else read(rel))
def filecheck(rel,sha,mode=None,size=None):
 p=safe(rel);raw=p.read_bytes();ck(digest(raw)==sha,'file '+rel)
 if mode is not None:ck(stat.S_IMODE(p.stat().st_mode)==mode,'mode '+rel)
 if size is not None:ck(len(raw)==size,'size '+rel)
 return raw
fd0=len(os.listdir('/proc/self/fd'))
audit=obj(T+'shared-build-0001/root-actual-documentation-review-0001.json','501685be1be4aad7805e88ed033bade09d3e876a323fa6f4a815cf4a85d15e28')
imp=obj(T+'shared-import-0001/application-receipt.json','a2213bfd843f496bbabb2bb65693c0dbc9dc6e25083d8ebffa7420e40992136e')
packet=obj(T+'shared-adoption-preparation-0001/application-inputs.json','c8c74a0954631a4b16fafe24fc4734272ab13506a9caac6161b34b221a3c54a1')
for k in ['website_selection_binding','website_handoff_binding','website_manifest_binding','website_peer_binding']:pin(**{ 'rel':packet[k]['path'],'sha':packet[k]['sha256']})
selection=obj(packet['website_selection_binding']['path'])['files'];ck(len(selection)==100,'selected100')
modes={r['target']:r for r in packet['target_modes']};ck(len(modes)==100,'modes100')
app=T+'shared-adoption-preparation-0001/applications/root-0001/'
applied=obj(app+'application-receipt.json');backup=obj(applied['backup_manifest']);journal=[json.loads(x) for x in read(applied['progress']).splitlines()]
ck(journal[0]['event']=='preflight-complete' and journal[1]=={'event':'all-preimages-durable','existing_backups':17},'durable-before-row order')
bytarget={r['target']:r for r in backup['files']};changed=[];unchanged=[]
ck(len(bytarget)==17 and len(set(backup['new_targets']))==83,'source backups/new target accounting')
for index,row in enumerate(selection):
 target=row['target'];ck(target.startswith(('website/','docs/lab/')) or target=='tooling/docs/import_site_docs.py','scope '+target)
 filecheck(row['postimage']['path'],row['postimage']['sha256'])
 filecheck(target,row['postimage']['sha256'],modes[target]['postimage_mode'])
 if row['preimage']['sha256'] is not None:
  old=bytarget[target];ck(old['sha256']==row['preimage']['sha256'] and old['mode']==modes[target]['preimage_mode'],'source original binding')
  filecheck(old['backup_path'],old['sha256'],old['mode'])
 else:ck(target in backup['new_targets'],'new source target')
 (changed if row['changed'] else unchanged).append(target)
ck(applied['changed']==changed and applied['unchanged']==unchanged and len(changed)==97 and len(unchanged)==3,'97 changed/3 same')
started=[r for r in journal if r['event']=='row-start'];done=[r for r in journal if r['event']=='row-complete']
ck([r['target'] for r in started]==changed and [r['target'] for r in done]==changed,'complete ordered effect ledger')
for a,b in zip(started,done):ck(a['index']==b['index'] and a['postimage_sha256']==b['postimage_sha256'],'ledger pair')
ck(journal[-1]=={'event':'complete','changed':97,'unchanged':3},'whole source effect complete')
# Fresh frozen implementation bytes, without executing any writer.
for directory,expected,count in [('shared-adoption-preparation-0001','2f9a17f28a0892006f3e2e2c7dce1ec409b53afdc415b2883648bbe294c64bc4',18),('website-integration-preparation-0001','a18906035ca9291d8609800c031271ab69c74e70b88277138da57006162495cc',163)]:
 held=obj(T+directory+'/source-manifest.json',expected)
 ck(len(held['files'])==count,'frozen selected implementation count')
 for r in held['files']:filecheck(r['path'],r['sha256'],size=r['size_bytes'])
filecheck(T+'shared-adoption-preparation-0001/adopt_reviewed_docs_v1.py','e9744320fece65fd404b222c39c385a81c6959ed8a530937b9a82800a1cc9692')
# Fresh table-byte audit only, with externally fixed pins and metadata-only path comparisons.
rows_total=external=0;targets=set(modes)
for role,b in packet['runtime_overlap_bindings'].items():
 table=obj(b['path'],b['sha256']);entries=table['files'];rows_total+=len(entries);role_external=0
 for r in entries:
  origin=r['path'];p=PurePosixPath(origin);ck(str(p)==origin and '..' not in p.parts,'captured origin canonical')
  if p.is_absolute():
   try:comparison=str(p.relative_to(ROOT))
   except ValueError:role_external+=1;continue
  else:comparison=origin
  ck(comparison not in targets,'runtime input overlap '+origin)
 external+=role_external
 receipt=next(v for v in applied['runtime_overlap_tables'] if v['role']==role)
 ck(receipt['captured_rows']==len(entries) and receipt['overlaps']==0 and receipt['absolute_external_declared_origins']==role_external,'overlap receipt')
ck(rows_total==35403 and external==751,'35403 rows/751 external origins')
summary['source_adoption']={'selected':100,'changed':97,'unchanged':3,'preimages':17,'new_targets':83,'overlap_rows':rows_total,'external_declared_origins_not_read':external,'overlap':0}
# Build preimages and unrelated artifact closure.
build=T+'shared-build-0001/'
preserved=obj(build+'output-preservation-receipt.json')
baseline=obj(preserved['selection_binding']['path'],preserved['selection_binding']['sha256'])
ck(preserved['files']==baseline['files'] and len(preserved['files'])==1137,'all build original declarations retained')
for r in preserved['files']:filecheck(build+'preimages/'+r['path'],r['sha256'],r['mode'],r['size_bytes'])
for r in preserved['unrelated_artifacts_retained']:filecheck(r['path'],r['sha256'])
ck(len(preserved['unrelated_artifacts_retained'])==5,'5 unrelated artifacts')
archive='website/artifacts/cyberalchemy-lab-website.zip'
pin(archive,'717659e32cf98aae6f6df1e180d60ba29ecbe2346cfc54b544122f0515c7cc3b')
with zipfile.ZipFile(safe(archive)) as z:
 names=z.namelist();ck(len(names)==len(set(names))==1214,'unique1214 archive files')
 for name in names:ck(z.read(name)==read('website/dist/'+name),'archive deployed bytes '+name)
manifest=obj('website/dist/release-manifest.json');ck(len(manifest['files'])==1213,'release1213 plus manifest')
for r in manifest['files']:filecheck('website/dist/'+r['path'],r['sha256'],size=r['bytes'])
summary['build']={'preimages':1137,'unrelated_unchanged':5,'archive_files':1214,'archive_matches_independently_reviewed_owned_build':True,'stages':10}
# Exact passive selection versus actual shared import, originals preserved before overwrite.
imports=T+'shared-import-0001/'
selected=obj(imports+'output-selection.json',imp['selection_sha256'])
filecheck('tooling/docs/import_site_docs.py',selected['importer_sha256'])
preserve=obj(imports+'preservation-receipt.json',imp['preservation_receipt_sha256'])
pin(imports+'terminal.log',imp['terminal_sha256'])
outputs={r['path']:r for r in selected['files']};ck(len(outputs)==631,'unique import631')
before=preserve['preimport_snapshot'];oldcount=0
for target,r in outputs.items():
 ck(target.startswith('docs/lab/'),'import closed scope')
 filecheck(target,r['sha256'],r['mode'],r['bytes'])
 if r['preimage_sha256'] is not None:
  oldcount+=1;ck(before[target]=={'sha256':r['preimage_sha256'],'mode':r['preimage_mode']},'import original pair')
  filecheck(imports+'preimages/'+target,r['preimage_sha256'],r['preimage_mode'])
 else:ck(target not in before,'new import target absent in preimport snapshot')
for target,r in before.items():
 if target not in outputs:filecheck(target,r['sha256'],r['mode'])
after={p.relative_to(ROOT).as_posix() for p in (ROOT/'docs/lab').rglob('*') if p.is_file()}
ck(after==set(before)|set(outputs),'no additional import outputs')
ck(oldcount==preserve['existing_outputs']==543 and len(set(before)-set(outputs))==210,'543 backups/210 unchanged')
importmanifest=obj('docs/lab/IMPORT-MANIFEST.json')
ck(len(importmanifest['pages'])==507 and len(importmanifest['assets'])==122 and importmanifest['unresolved_links']==[],'507/122/unresolved0')
for r in importmanifest['pages']:
 filecheck('docs/lab/'+r['output'],r['output_sha256'])
 source=(ROOT/'website/dist/governance-lab-series'/r['source']).resolve()
 ck(source.is_relative_to(ROOT/'website/dist'),'import source outside selected static deployment')
 filecheck(source.relative_to(ROOT).as_posix(),r['source_sha256'])
for r in importmanifest['assets']:filecheck('docs/lab/'+r['path'],r['sha256'])
comp={'matching':0,'different':0,'unavailable':0};digest_bearing=0
for r in importmanifest['record_sources']:
 raw=read(r['path']);ck(digest(raw)==r['repository_sha256'],'catalog repository comparison')
 if r['repository_sha256'] is None:comp['unavailable']+=1
 if r.get('captured_sha256'):
  digest_bearing+=1
  ck(r['matches_capture']==(r['repository_sha256']==r['captured_sha256']),'catalog boolean')
  comp['matching' if r['matches_capture'] else 'different']+=1
ck(comp=={'matching':345,'different':0,'unavailable':0} and comp==selected['source_comparison_counts']==importmanifest['source_comparison_counts'],'truthful current catalog345 comparison')
# Runtime route closure: Markdown parser ignores code and inert downloaded snapshots.
md=MarkdownIt();routes=obj('website/dist/governance-lab-series/research/runtime-pages.json')['pages'];ck(len(routes)==14,'runtime14')
local=0
for page in routes:
 target='docs/lab/runtime/'+page['markdown_route'];raw=read(target);ck(target in outputs,'runtime route selected')
 for token in md.parse(raw.decode()):
  for child in token.children or []:
   if child.type not in ('link_open','image'):continue
   href=child.attrGet('href' if child.type=='link_open' else 'src');u=urlsplit(href)
   if u.scheme or u.netloc or not u.path:continue
   local+=1;link=(safe(target).parent/unquote(u.path)).resolve();ck(link.is_relative_to(ROOT) and link.is_file(),'runtime local link '+target+' -> '+href)
ck(local==236,'runtime236 local links')
summary['import']={'pages':507,'assets':122,'selected_outputs':631,'preimages':543,'unselected_unchanged':210,'runtime_routes':14,'runtime_local_links':local,'catalog_records':454,'digest_bearing_matches':digest_bearing,'source_comparison_counts':comp}
for p in [T+'shared-adoption-preparation-0001/adopt_reviewed_docs_v1.py',imports+'collect_outputs.py',imports+'apply_import.py',build+'terminal.log',build+'output-preservation-receipt.json',app+'application-receipt.json',app+'backup-manifest.json',app+'progress.jsonl']:
 bindings.append({'path':p,'sha256':digest(read(p))})
ck(len(os.listdir('/proc/self/fd'))==fd0,'file descriptor balance')
result={'schema_version':'lab-T21-actual-shared-docs-independent-controls/v1','result':'PASS','authority_effect':'none','checks':checks,'fd_delta':0,'summary':summary,'bindings':bindings,'actual_build_import_or_shared_writes':False,'Lab_runtime_or_private_access':False,'full_T21_complete':False}
print(json.dumps(result,sort_keys=True,indent=2))
