"""Freeze tested source bytes, excluding build outputs. See README.md."""
import hashlib,json,tarfile
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/essays-implementation-package-0071'
files=sorted(p for p in W.rglob('*') if p.is_file() and not {'target','__pycache__'}.intersection(p.relative_to(W).parts))
manifest=[{'path':str(p.relative_to(W)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
(H/'package-inputs.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
with tarfile.open(H/'package-snapshot.tar.gz','w:gz') as a:
 for p in files:a.add(p,arcname=str(p.relative_to(W)),recursive=False)
print('Frozen',len(files),'source files.')
