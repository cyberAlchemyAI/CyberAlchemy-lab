"""Explicit preserved-base successor selection and public documentation postimages."""
from common import *
import shutil
CONTROL=Path(__file__).resolve().parent;HERE=CONTROL.parents[1];ROOT=HERE.parents[5];OUT=HERE/'packages/0002'
BASE='882957b3f17bcc5ec195491eeefabbe5c7f9909308ed89bedad2186e2a38a72c'

def run():
 raw=read(HERE/'source-manifest.json');need(sha(raw)==BASE,'preserved predecessor manifest differs');base=parse(raw)
 for b in base['files']:need(sha(read(ROOT/b['path']))==b['sha256'],'preserved predecessor changed')
 need(not OUT.exists() and not (CONTROL/'source-manifest.json').exists(),'preserve successor package')
 old=HERE/'packages/0001';v=load(old/'selection.json');source=payload(read(old/'payload.snapshot'))
 for name in ['installer.py','DESIGN.md','OPERATIONS.md']:
  source[(HERE/name).relative_to(ROOT).as_posix()]=read(CONTROL/name)
 OUT.mkdir();(OUT/'wheels').mkdir()
 for p in (old/'wheels').iterdir():shutil.copyfile(p,OUT/'wheels'/p.name)
 raw=encoded(snapshot(source));(OUT/'payload.snapshot').write_bytes(raw)
 v['snapshot_sha256']=sha(raw);v['limitations'].append('Source repository state remains separately pinned outside package; public evidence excludes baseline; protected archives never enter distributable outputs.')
 emit(OUT/'selection.json',v)
 files={b['path']:b['sha256'] for b in base['files']};files[(HERE/'source-manifest.json').relative_to(ROOT).as_posix()]=BASE
 for p in list(CONTROL.iterdir())+list(OUT.rglob('*')):
  if p.is_file():files[p.relative_to(ROOT).as_posix()]=sha(read(p))
 manifest={**base,'schema_version':'lab-R02-source-closure/v2-candidate','files':[{'path':n,'sha256':h} for n,h in sorted(files.items())],'package_binding':{'path':str((OUT/'selection.json').relative_to(ROOT)),'sha256':sha(read(OUT/'selection.json'))},'preserved_predecessor':{'path':str((HERE/'source-manifest.json').relative_to(ROOT)),'sha256':BASE},'selected_successor':'Public code/control package with separate source repository, protected full history recovery and private candidate scope parents.'}
 emit(CONTROL/'source-manifest.json',manifest);print(json.dumps({'result':'PASS','files':len(files),'source_files':len(source),'package_sha256':sha(read(OUT/'selection.json')),'manifest_sha256':sha(read(CONTROL/'source-manifest.json'))}))
if __name__=='__main__':run()
