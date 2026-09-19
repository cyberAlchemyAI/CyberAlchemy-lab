"""Pin existing runtime source and verified People and Teams bytes. See README.md."""
import hashlib,json,shutil,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/people-teams-runtime-package-0074';runtime=R/'implementation/bindings/ontology-product-event-runtime/v4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['Cargo.toml','Cargo.lock','README.md','src','tests']:
 src=runtime/name;dst=W/'runtime'/name
 if src.is_dir():shutil.copytree(src,dst,dirs_exist_ok=True)
 else:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
shutil.copytree(R/'.local/ontology-context-import-0072/package',W/'source',dirs_exist_ok=True)
plan=json.loads((H.parent/'0073-existing-runtime-gap-review/people-teams-plan.json').read_text());plan['roots']['people72']=str(W/'source')
(H/'runtime-manifest.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n')
files=sorted(p for p in W.rglob('*') if p.is_file());(H/'package-inputs.json').write_text(json.dumps([{'path':str(p.relative_to(W)),'sha256':sha(p)} for p in files],indent=2,sort_keys=True)+'\n')
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('Pinned',len(files),'files.')
